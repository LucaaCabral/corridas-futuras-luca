from ..normalizar import NOMES_UF
from .base import Fonte

# PENDENTE DE VALIDAÇÃO: padrões de URL definidos sem acesso ao site.
# O site organiza o calendário por estado (ex.: /saopaulo, /riodejaneiro).
# Valide com: python -m coletor --fontes brasilquecorre --salvar-html /tmp/bqc


class BrasilQueCorre(Fonte):
    nome = "brasilquecorre"
    site = "https://brasilquecorre.com"
    padrao_link_evento = r"brasilquecorre\.com/[a-z]+/[^/?#]+"

    def urls_listagem(self):
        for nome in sorted(NOMES_UF):
            yield f"{self.site}/{nome.replace(' ', '')}"
