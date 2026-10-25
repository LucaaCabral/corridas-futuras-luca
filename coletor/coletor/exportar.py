"""Grava os JSONs consumidos pelo front-end em web/public/data/."""

import json
import shutil
from datetime import date
from pathlib import Path

from .config import DADOS, SAIDA_WEB
from .modelo import Corrida
from .normalizar import agora_iso


def exportar(corridas: list[Corrida], relatorio_fontes: dict[str, dict], destino: Path = SAIDA_WEB) -> dict:
    """Escreve um arquivo por UF + indice.json e copia a base de municípios.

    Corridas com data anterior a hoje são descartadas. Os arquivos de UF que
    ficarem sem corridas são removidos, para não exibir dados antigos.
    """
    hoje = date.today().isoformat()
    por_uf: dict[str, list[dict]] = {}
    for c in corridas:
        if c.data >= hoje:
            por_uf.setdefault(c.uf, []).append(c.para_dict())

    pasta_ufs = destino / "corridas"
    pasta_ufs.mkdir(parents=True, exist_ok=True)
    for antigo in pasta_ufs.glob("*.json"):
        if antigo.stem not in por_uf:
            antigo.unlink()
    for uf, lista in por_uf.items():
        _gravar(pasta_ufs / f"{uf}.json", lista)

    indice = {
        "gerado_em": agora_iso(),
        "total": sum(len(v) for v in por_uf.values()),
        "por_uf": {uf: len(v) for uf, v in sorted(por_uf.items())},
        "fontes": relatorio_fontes,
    }
    _gravar(destino / "indice.json", indice, compacto=False)

    for nome in ("municipios.json", "estados.json"):
        shutil.copyfile(DADOS / nome, destino / nome)
    return indice


def _gravar(caminho: Path, dados, compacto: bool = True) -> None:
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":")) if compacto else json.dumps(
        dados, ensure_ascii=False, indent=2
    )
    caminho.write_text(texto, encoding="utf-8")
