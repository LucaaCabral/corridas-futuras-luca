"""Regenera dados/municipios.json e dados/estados.json a partir da base
pública kelvins/municipios-brasileiros (códigos e coordenadas do IBGE).

Uso: python coletor/scripts/gerar_municipios.py
"""

import json
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/json/"
DADOS = Path(__file__).resolve().parents[2] / "dados"


def baixar(nome: str) -> list[dict]:
    with urllib.request.urlopen(BASE + nome, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


def main() -> None:
    estados = {e["codigo_uf"]: e for e in baixar("estados.json")}
    municipios = sorted(
        (
            {
                "id": m["codigo_ibge"],
                "nome": m["nome"],
                "uf": estados[m["codigo_uf"]]["uf"],
                "lat": round(m["latitude"], 4),
                "lon": round(m["longitude"], 4),
            }
            for m in baixar("municipios.json")
        ),
        key=lambda m: (m["uf"], m["nome"]),
    )
    ufs = sorted(({"uf": e["uf"], "nome": e["nome"]} for e in estados.values()), key=lambda e: e["nome"])

    DADOS.mkdir(exist_ok=True)
    (DADOS / "municipios.json").write_text(
        json.dumps(municipios, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (DADOS / "estados.json").write_text(json.dumps(ufs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(municipios)} municípios, {len(ufs)} estados")


if __name__ == "__main__":
    main()
