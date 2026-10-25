from .base import Fonte

# PENDENTE DE VALIDAÇÃO: padrões de URL definidos sem acesso ao site.
# A listagem da Sympla é renderizada em JavaScript; se a página vier sem links,
# o caminho é usar a API JSON que o próprio site chama (ver aba Rede do navegador).
# Valide com: python -m coletor --fontes sympla --salvar-html /tmp/sympla


class Sympla(Fonte):
    nome = "sympla"
    site = "https://www.sympla.com.br"
    padrao_link_evento = r"sympla\.com\.br/evento/"

    def urls_listagem(self):
        for pagina in range(1, 11):
            yield f"{self.site}/eventos/esportes?s=corrida&page={pagina}"
