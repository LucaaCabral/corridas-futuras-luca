from ..normalizar import UFS
from .base import Fonte

# PENDENTE DE VALIDAÇÃO: padrões de URL definidos sem acesso ao site.
# Valide com: python -m coletor --fontes corridasbrasil --salvar-html /tmp/cb


class CorridasBrasil(Fonte):
    nome = "corridasbrasil"
    site = "https://www.corridasbrasil.com.br"
    padrao_link_evento = r"corridasbrasil\.com\.br/.*(corrida|evento)"

    def urls_listagem(self):
        for uf in sorted(UFS):
            yield f"{self.site}/calendario/{uf.lower()}"
