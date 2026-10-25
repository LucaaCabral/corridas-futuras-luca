"""CLI do coletor.

    python -m coletor                       # coleta todas as fontes e exporta
    python -m coletor --fontes sympla       # coleta só uma (as demais vêm do cache)
    python -m coletor --so-exportar         # reexporta a partir do cache, sem acessar os sites
    python -m coletor --salvar-html /tmp/x  # salva o HTML baixado (para depurar/criar fixtures)
"""

import argparse
import logging
from pathlib import Path

from . import cache
from .dedup import consolidar
from .exportar import exportar
from .fontes import FONTES, Cliente
from .geo import base_padrao
from .normalizar import agora_iso

log = logging.getLogger("coletor")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coletor", description="Coleta corridas de rua e exporta para o site.")
    parser.add_argument("--fontes", nargs="+", choices=sorted(FONTES), help="fontes a coletar (padrão: todas)")
    parser.add_argument("--so-exportar", action="store_true", help="não acessa os sites; usa só o cache")
    parser.add_argument("--salvar-html", type=Path, metavar="PASTA", help="salva as páginas baixadas")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    a_coletar = [] if args.so_exportar else (args.fontes or sorted(FONTES))
    relatorio: dict[str, dict] = {}

    if a_coletar:
        cliente = Cliente(salvar_em=args.salvar_html)
        try:
            for nome in a_coletar:
                log.info("Coletando %s...", nome)
                try:
                    corridas = FONTES[nome](cliente).coletar()
                except Exception as erro:  # uma fonte quebrada não derruba as outras
                    log.exception("Falha em %s", nome)
                    relatorio[nome] = {"ok": False, "erro": f"{type(erro).__name__}: {erro}"}
                    continue
                log.info("  %d corridas encontradas", len(corridas))
                if corridas:
                    cache.salvar(nome, corridas)
                    relatorio[nome] = {"ok": True, "coletado_em": agora_iso()}
                else:
                    # Zero resultados quase sempre significa que o site mudou; mantém o cache anterior.
                    relatorio[nome] = {"ok": False, "erro": "nenhuma corrida encontrada"}
        finally:
            cliente.fechar()

    brutas = []
    for nome in sorted(FONTES):
        corridas, coletado_em = cache.carregar(nome)
        brutas.extend(corridas)
        info = relatorio.setdefault(nome, {"ok": coletado_em is not None})
        info["coletado_em"] = info.get("coletado_em") or coletado_em
        info["total"] = len(corridas)

    consolidadas, descartadas = consolidar(brutas, base_padrao())
    if descartadas:
        log.warning("%d corridas descartadas por cidade não localizada (use -v para detalhes)", descartadas)
    indice = exportar(consolidadas, relatorio)
    log.info("Exportadas %d corridas futuras em %d estados.", indice["total"], len(indice["por_uf"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
