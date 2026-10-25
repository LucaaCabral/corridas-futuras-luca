"""Funções para transformar textos dos sites em valores estruturados."""

import re
import unicodedata
from datetime import date, datetime

MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

NOMES_UF = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA",
    "ceara": "CE", "distrito federal": "DF", "espirito santo": "ES", "goias": "GO",
    "maranhao": "MA", "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
    "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE", "piaui": "PI",
    "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS",
    "rondonia": "RO", "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP",
    "sergipe": "SE", "tocantins": "TO",
}


def sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sem acentos, sem pontuação e com espaços simples."""
    texto = sem_acentos(texto).lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return texto.strip()


def parse_data(texto: str | None) -> date | None:
    if not texto:
        return None
    texto = texto.strip()

    # ISO: 2026-11-15 ou 2026-11-15T07:00:00-03:00
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", texto)
    if m:
        return _data_segura(int(m[1]), int(m[2]), int(m[3]))

    # 15/11/2026 ou 15-11-2026 ou 15.11.26
    m = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", texto)
    if m:
        ano = int(m[3])
        ano += 2000 if ano < 100 else 0
        return _data_segura(ano, int(m[2]), int(m[1]))

    # 15 de novembro de 2026 / 15 nov 2026 / 15 NOV. 2026
    m = re.search(r"(\d{1,2})\s*(?:de\s+)?([a-zç]{3})[a-zç]*\.?\s*(?:de\s+)?(\d{4})", sem_acentos(texto).lower())
    if m and m[2] in MESES:
        return _data_segura(int(m[3]), MESES[m[2]], int(m[1]))

    return None


def _data_segura(ano: int, mes: int, dia: int) -> date | None:
    try:
        return date(ano, mes, dia)
    except ValueError:
        return None


_RE_DISTANCIA = re.compile(r"(\d{1,3}(?:[.,]\d{1,3})?)\s*(km|k)\b", re.IGNORECASE)


def parse_distancias(*textos: str | None) -> list[float]:
    """Extrai distâncias em km de textos livres ("5K e 10K", "21,1 km", "Meia Maratona")."""
    encontradas: set[float] = set()
    for texto in textos:
        if not texto:
            continue
        for numero, _ in _RE_DISTANCIA.findall(texto):
            valor = float(numero.replace(",", "."))
            if 0.5 <= valor <= 250:
                encontradas.add(round(valor, 3))
        plano = normalizar_texto(texto)
        if re.search(r"\bmeia maratona\b|\bhalf marathon\b", plano):
            encontradas.add(21.1)
        if re.search(r"(?<!meia )\bmaratona\b|\bmarathon\b", plano.replace("meia maratona", "")):
            encontradas.add(42.195)
    return sorted(encontradas)


def parse_preco(valor: str | float | int | None) -> float | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    # Ordem importa: "1.250,00" (BR), "119.90" (ponto decimal), "1.250" (milhar).
    m = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{1,2}|\d+\.\d{1,2}(?!\d)|\d{1,3}(?:\.\d{3})+|\d+)", valor)
    if not m:
        return None
    numero = m[1]
    if "," in numero or re.fullmatch(r"\d{1,3}(?:\.\d{3})+", numero):
        numero = numero.replace(".", "").replace(",", ".")
    try:
        return float(numero)
    except ValueError:
        return None


def parse_uf(texto: str | None) -> str | None:
    if not texto:
        return None
    sigla = texto.strip().upper()
    if sigla in UFS:
        return sigla
    return NOMES_UF.get(normalizar_texto(texto))


def separar_cidade_uf(texto: str | None) -> tuple[str | None, str | None]:
    """'Campinas - SP', 'Campinas/SP', 'Campinas, SP' -> ('Campinas', 'SP')."""
    if not texto:
        return None, None
    texto = texto.strip()
    m = re.match(r"^(.*?)\s*[-/,–|]\s*([A-Za-z]{2})\s*$", texto)
    if m and m[2].upper() in UFS:
        return m[1].strip(), m[2].upper()
    return texto, None


def agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
