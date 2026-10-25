"""Guarda o último resultado bem-sucedido de cada fonte.

Assim, rodar só uma fonte (ou uma fonte falhar) não apaga as corridas das outras.
"""

import json
from datetime import date
from pathlib import Path

from .config import RAIZ
from .modelo import CorridaBruta
from .normalizar import agora_iso

PASTA = RAIZ / "coletor" / ".cache"


def salvar(fonte: str, corridas: list[CorridaBruta], pasta: Path = PASTA) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    dados = {
        "coletado_em": agora_iso(),
        "corridas": [{**c.__dict__, "data": c.data.isoformat()} for c in corridas],
    }
    (pasta / f"{fonte}.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def carregar(fonte: str, pasta: Path = PASTA) -> tuple[list[CorridaBruta], str | None]:
    arquivo = pasta / f"{fonte}.json"
    if not arquivo.exists():
        return [], None
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    corridas = [CorridaBruta(**{**c, "data": date.fromisoformat(c["data"])}) for c in dados["corridas"]]
    return corridas, dados["coletado_em"]
