"""Localiza cidades na base de municípios do IBGE (sem chamadas externas)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import DADOS
from .normalizar import normalizar_texto


@dataclass(frozen=True)
class Municipio:
    id: int
    nome: str
    uf: str
    lat: float
    lon: float


class BaseMunicipios:
    def __init__(self, municipios: list[Municipio]):
        self._por_nome_uf: dict[tuple[str, str], Municipio] = {}
        self._por_nome: dict[str, list[Municipio]] = {}
        for m in municipios:
            chave = normalizar_texto(m.nome)
            self._por_nome_uf[(chave, m.uf)] = m
            self._por_nome.setdefault(chave, []).append(m)

    @classmethod
    def carregar(cls, caminho: Path = DADOS / "municipios.json") -> "BaseMunicipios":
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return cls([Municipio(**m) for m in dados])

    def localizar(self, cidade: str | None, uf: str | None) -> Municipio | None:
        if not cidade:
            return None
        chave = normalizar_texto(cidade)
        if uf:
            return self._por_nome_uf.get((chave, uf.upper()))
        candidatos = self._por_nome.get(chave, [])
        # Sem UF, só aceitamos quando o nome é único no país.
        return candidatos[0] if len(candidatos) == 1 else None


@lru_cache(maxsize=1)
def base_padrao() -> BaseMunicipios:
    return BaseMunicipios.carregar()
