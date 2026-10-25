from ..normalizar import UFS
from .base import Fonte

# PENDENTE DE VALIDAÇÃO: padrões de URL definidos sem acesso ao site.
# Valide com: python -m coletor --fontes ticketsports --salvar-html /tmp/ts


class TicketSports(Fonte):
    nome = "ticketsports"
    site = "https://www.ticketsports.com.br"
    padrao_link_evento = r"ticketsports\.com\.br/e/"

    def urls_listagem(self):
        for uf in sorted(UFS):
            yield f"{self.site}/Calendario/Todos-os-organizadores/Corrida-de-rua/{uf}/"
