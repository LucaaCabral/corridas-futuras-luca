"""Infraestrutura comum às fontes: cliente HTTP educado e extração de JSON-LD.

A maioria dos sites de inscrição publica os eventos em JSON-LD (schema.org
Event/SportsEvent) para SEO. Por isso a estratégia padrão de uma fonte é:

1. baixar as páginas de listagem/calendário;
2. extrair eventos JSON-LD presentes nelas;
3. se a listagem não tiver JSON-LD, seguir os links de eventos e extrair de cada página.

Fontes que exponham uma API JSON própria podem sobrescrever `coletar()`.
"""

import json
import logging
import re
import time
from collections.abc import Iterable, Iterator
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from .. import config
from ..modelo import CorridaBruta
from ..normalizar import parse_data, parse_distancias, parse_preco, parse_uf, separar_cidade_uf

log = logging.getLogger(__name__)

TIPOS_EVENTO = {"event", "sportsevent"}


class Cliente:
    """httpx com user-agent identificável, robots.txt e intervalo entre requisições."""

    def __init__(self, salvar_em: Path | None = None):
        self._http = httpx.Client(
            headers={"User-Agent": config.USER_AGENT, "Accept-Language": "pt-BR,pt;q=0.9"},
            timeout=config.TIMEOUT_S,
            follow_redirects=True,
        )
        self._robots: dict[str, RobotFileParser | None] = {}
        self._ultima: dict[str, float] = {}
        self._salvar_em = salvar_em

    def _permitido(self, url: str) -> bool:
        host = urlparse(url).netloc
        if host not in self._robots:
            rp = RobotFileParser()
            try:
                resp = self._http.get(f"{urlparse(url).scheme}://{host}/robots.txt")
                rp.parse(resp.text.splitlines() if resp.status_code == 200 else [])
                self._robots[host] = rp
            except httpx.HTTPError:
                self._robots[host] = None  # sem robots.txt acessível: segue com cautela
        rp = self._robots[host]
        return rp is None or rp.can_fetch(config.USER_AGENT, url)

    def get(self, url: str) -> str | None:
        if not self._permitido(url):
            log.warning("robots.txt não permite %s", url)
            return None
        host = urlparse(url).netloc
        espera = config.INTERVALO_S - (time.monotonic() - self._ultima.get(host, 0))
        if espera > 0:
            time.sleep(espera)
        try:
            resp = self._http.get(url)
        finally:
            self._ultima[host] = time.monotonic()
        if resp.status_code != 200:
            log.warning("HTTP %s em %s", resp.status_code, url)
            return None
        if self._salvar_em:
            self._salvar(url, resp.text)
        return resp.text

    def _salvar(self, url: str, html: str) -> None:
        nome = re.sub(r"[^A-Za-z0-9]+", "_", url.split("://", 1)[-1])[:150] + ".html"
        self._salvar_em.mkdir(parents=True, exist_ok=True)
        (self._salvar_em / nome).write_text(html, encoding="utf-8")

    def fechar(self) -> None:
        self._http.close()


# --------------------------------------------------------------------------- JSON-LD


def _tipos(obj: dict) -> set[str]:
    tipo = obj.get("@type", [])
    tipos = tipo if isinstance(tipo, list) else [tipo]
    return {str(t).lower() for t in tipos}


def _achatar(dado) -> Iterator[dict]:
    if isinstance(dado, list):
        for item in dado:
            yield from _achatar(item)
    elif isinstance(dado, dict):
        yield dado
        for chave in ("@graph", "itemListElement", "item", "subEvent"):
            if chave in dado:
                yield from _achatar(dado[chave])


def eventos_jsonld(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    eventos = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            dado = json.loads(script.string or script.get_text() or "")
        except json.JSONDecodeError:
            continue
        eventos.extend(obj for obj in _achatar(dado) if _tipos(obj) & TIPOS_EVENTO)
    return eventos


def _texto(valor) -> str | None:
    if isinstance(valor, dict):
        return valor.get("name") or valor.get("@id")
    if isinstance(valor, list):
        return _texto(valor[0]) if valor else None
    return str(valor) if valor is not None else None


def _cidade_uf(evento: dict) -> tuple[str | None, str | None]:
    local = evento.get("location")
    if isinstance(local, list):
        local = local[0] if local else None
    if not isinstance(local, dict):
        return separar_cidade_uf(_texto(local))

    endereco = local.get("address")
    if isinstance(endereco, dict):
        cidade = endereco.get("addressLocality")
        uf = parse_uf(_texto(endereco.get("addressRegion")))
        if cidade:
            cidade_sep, uf_sep = separar_cidade_uf(cidade)
            return cidade_sep, uf or uf_sep
    elif isinstance(endereco, str):
        # "Rua X, 100 - Centro, Campinas - SP, 13000-000": procura "Cidade - UF".
        m = re.search(r"([A-Za-zÀ-ú' .]+?)\s*[-/]\s*([A-Z]{2})\b", endereco)
        if m:
            return m[1].strip(" ,"), parse_uf(m[2])
    return separar_cidade_uf(local.get("name"))


def _preco(evento: dict) -> float | None:
    ofertas = evento.get("offers")
    ofertas = ofertas if isinstance(ofertas, list) else [ofertas] if ofertas else []
    precos = []
    for o in ofertas:
        if isinstance(o, dict):
            for chave in ("lowPrice", "price"):
                p = parse_preco(o.get(chave))
                if p is not None:
                    precos.append(p)
                    break
    positivos = [p for p in precos if p > 0]
    return min(positivos) if positivos else (0.0 if precos else None)


def jsonld_para_corrida(evento: dict, fonte: str, url_pagina: str) -> CorridaBruta | None:
    nome = _texto(evento.get("name"))
    data = parse_data(_texto(evento.get("startDate")))
    if not nome or not data:
        return None
    cidade, uf = _cidade_uf(evento)
    url = urljoin(url_pagina, _texto(evento.get("url")) or url_pagina)
    return CorridaBruta(
        nome=nome.strip(),
        data=data,
        url=url,
        fonte=fonte,
        cidade=cidade,
        uf=uf,
        distancias_km=parse_distancias(nome, _texto(evento.get("description"))),
        preco_min=_preco(evento),
    )


# --------------------------------------------------------------------------- Fonte


class Fonte:
    """Fonte genérica baseada em JSON-LD. Subclasses definem URLs e padrões de link."""

    nome: str = ""
    site: str = ""
    # Regex que identifica links para páginas de evento dentro das listagens.
    padrao_link_evento: str | None = None
    # Palavras que, se presentes no nome/descrição, indicam que é corrida.
    filtro_corrida = re.compile(r"corrida|run\b|maratona|marathon|\b\d+\s*k(m)?\b|trail|rústica|rustica", re.I)

    def __init__(self, cliente: Cliente):
        self.cliente = cliente

    def urls_listagem(self) -> Iterable[str]:
        raise NotImplementedError

    def coletar(self) -> list[CorridaBruta]:
        corridas: list[CorridaBruta] = []
        links_evento: list[str] = []
        vistos: set[str] = set()

        for i, url in enumerate(self.urls_listagem()):
            if i >= config.MAX_PAGINAS_LISTAGEM:
                break
            html = self.cliente.get(url)
            if not html:
                continue
            achadas = self._de_jsonld(html, url)
            corridas.extend(achadas)
            if not achadas and self.padrao_link_evento:
                for link in self._links_evento(html, url):
                    if link not in vistos:
                        vistos.add(link)
                        links_evento.append(link)

        for url in links_evento[: config.MAX_PAGINAS_EVENTO]:
            html = self.cliente.get(url)
            if html:
                corridas.extend(self._de_jsonld(html, url))

        return [c for c in corridas if self.eh_corrida(c)]

    def eh_corrida(self, corrida: CorridaBruta) -> bool:
        return bool(corrida.distancias_km) or bool(self.filtro_corrida.search(corrida.nome))

    def _de_jsonld(self, html: str, url: str) -> list[CorridaBruta]:
        return [c for e in eventos_jsonld(html) if (c := jsonld_para_corrida(e, self.nome, url))]

    def _links_evento(self, html: str, url_base: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        padrao = re.compile(self.padrao_link_evento)
        links = []
        for a in soup.find_all("a", href=True):
            absoluto = urljoin(url_base, a["href"]).split("#")[0]
            if padrao.search(absoluto) and absoluto not in links:
                links.append(absoluto)
        return links
