from coletor.fontes.base import Fonte, eventos_jsonld, jsonld_para_corrida


def test_extrai_eventos_jsonld(fixture_html):
    eventos = eventos_jsonld(fixture_html("listagem_jsonld.html"))
    assert [e["name"] for e in eventos] == ["Corrida Noturna 5K e 10K", "Meia Maratona de Jundiaí", "Show de Rock"]


def test_converte_jsonld_em_corrida(fixture_html):
    url = "https://www.exemplo.com.br/calendario"
    corridas = [jsonld_para_corrida(e, "teste", url) for e in eventos_jsonld(fixture_html("listagem_jsonld.html"))]
    noturna, meia, show = corridas
    assert (noturna.cidade, noturna.uf) == ("Campinas", "SP")
    assert noturna.distancias_km == [5.0, 10.0]
    assert noturna.preco_min == 89.9
    assert noturna.url == "https://www.exemplo.com.br/e/corrida-noturna-123"
    assert (meia.cidade, meia.uf, meia.distancias_km, meia.preco_min) == ("Jundiaí", "SP", [21.1], 150.0)
    assert meia.url == url
    assert show.uf == "SP"


class ClienteFalso:
    def __init__(self, paginas):
        self.paginas = paginas
        self.pedidas = []

    def get(self, url):
        self.pedidas.append(url)
        return self.paginas.get(url)


class FonteTeste(Fonte):
    nome = "teste"
    padrao_link_evento = r"/e/"

    def urls_listagem(self):
        return ["https://x.com/lista", "https://x.com/fora-do-ar"]


def test_coletar_segue_links_quando_listagem_nao_tem_jsonld(fixture_html):
    cliente = ClienteFalso({
        "https://x.com/lista": fixture_html("listagem_links.html"),
        "https://x.com/e/corrida-noturna-123": fixture_html("listagem_jsonld.html"),
    })
    corridas = FonteTeste(cliente).coletar()
    # Link duplicado (com âncora) só é visitado uma vez; "Show de Rock" é filtrado.
    assert cliente.pedidas.count("https://x.com/e/corrida-noturna-123") == 1
    assert sorted(c.nome for c in corridas) == ["Corrida Noturna 5K e 10K", "Meia Maratona de Jundiaí"]
