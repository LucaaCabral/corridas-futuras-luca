from ..normalizar import UFS
from .base import Fonte

# PENDENTE DE VALIDAÇÃO: padrões de URL definidos sem acesso ao site.
# Valide com: python -m coletor --fontes minhasinscricoes --salvar-html /tmp/mi


class MinhasInscricoes(Fonte):
    nome = "minhasinscricoes"
    site = "https://www.minhasinscricoes.com.br"
    padrao_link_evento = r"(?i)minhasinscricoes\.com\.br/.*evento/"

    def urls_listagem(self):
        for uf in sorted(UFS):
            yield f"{self.site}/pt-br/calendario?estado={uf}&modalidade=corrida"
