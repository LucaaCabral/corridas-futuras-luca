"""Converte corridas brutas em corridas localizadas e une duplicatas entre fontes."""

import logging
from difflib import SequenceMatcher

from .geo import BaseMunicipios
from .modelo import Corrida, CorridaBruta, Link
from .normalizar import normalizar_texto

log = logging.getLogger(__name__)

# Palavras que variam entre sites para a mesma prova e atrapalham a comparação.
_RUIDO = {
    "corrida", "de", "da", "do", "das", "dos", "e", "a", "o", "rua", "run", "km", "k",
    "edicao", "ed", "2025", "2026", "2027", "2028",
}
SIMILARIDADE_MINIMA = 0.8


def _nome_comparavel(nome: str) -> str:
    return " ".join(p for p in normalizar_texto(nome).split() if p not in _RUIDO and not p.isdigit())


def _mesma_corrida(a: str, b: str) -> bool:
    a, b = _nome_comparavel(a), _nome_comparavel(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= SIMILARIDADE_MINIMA


def consolidar(brutas: list[CorridaBruta], base: BaseMunicipios) -> tuple[list[Corrida], int]:
    """Retorna (corridas consolidadas, quantidade descartada por cidade não localizada)."""
    grupos: dict[tuple[str, int], list[Corrida]] = {}
    descartadas = 0

    for b in brutas:
        municipio = base.localizar(b.cidade, b.uf)
        if municipio is None:
            descartadas += 1
            log.debug("Cidade não localizada: %r/%r (%s)", b.cidade, b.uf, b.url)
            continue

        data = b.data.isoformat()
        link = Link(fonte=b.fonte, url=b.url)
        mesmo_dia_cidade = grupos.setdefault((data, municipio.id), [])

        existente = next((c for c in mesmo_dia_cidade if _mesma_corrida(c.nome, b.nome)), None)
        if existente:
            existente.distancias_km = sorted(set(existente.distancias_km) | set(b.distancias_km))
            precos = [p for p in (existente.preco_min, b.preco_min) if p is not None]
            existente.preco_min = min(precos) if precos else None
            if all(l.url != link.url for l in existente.links):
                existente.links.append(link)
            continue

        mesmo_dia_cidade.append(
            Corrida(
                id=Corrida.gerar_id(b.nome, data, municipio.id),
                nome=b.nome.strip(),
                data=data,
                cidade=municipio.nome,
                uf=municipio.uf,
                codigo_ibge=municipio.id,
                lat=municipio.lat,
                lon=municipio.lon,
                distancias_km=sorted(set(b.distancias_km)),
                preco_min=b.preco_min,
                links=[link],
            )
        )

    corridas = [c for grupo in grupos.values() for c in grupo]
    corridas.sort(key=lambda c: (c.data, c.nome))
    return corridas, descartadas
