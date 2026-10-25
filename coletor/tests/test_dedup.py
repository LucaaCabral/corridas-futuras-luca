from datetime import date

from coletor.dedup import consolidar
from coletor.geo import base_padrao
from coletor.modelo import CorridaBruta


def bruta(nome, fonte, url, cidade="Campinas", uf="SP", dia=15, dist=(5.0,), preco=None):
    return CorridaBruta(nome=nome, data=date(2099, 11, dia), url=url, fonte=fonte,
                        cidade=cidade, uf=uf, distancias_km=list(dist), preco_min=preco)


def test_une_mesma_corrida_de_fontes_diferentes():
    corridas, descartadas = consolidar([
        bruta("Corrida Noturna de Campinas 2099", "a", "https://a/1", dist=(5,), preco=100),
        bruta("Noturna de Campinas", "b", "https://b/1", dist=(10,), preco=80),
    ], base_padrao())
    assert descartadas == 0
    assert len(corridas) == 1
    c = corridas[0]
    assert c.distancias_km == [5, 10]
    assert c.preco_min == 80
    assert [l.fonte for l in c.links] == ["a", "b"]
    assert (c.cidade, c.uf, c.codigo_ibge) == ("Campinas", "SP", 3509502)


def test_nao_une_datas_ou_nomes_diferentes():
    corridas, _ = consolidar([
        bruta("Corrida Noturna", "a", "https://a/1"),
        bruta("Corrida Noturna", "a", "https://a/2", dia=16),
        bruta("Desafio das Serras", "a", "https://a/3"),
    ], base_padrao())
    assert len(corridas) == 3


def test_descarta_cidade_desconhecida():
    corridas, descartadas = consolidar([bruta("X", "a", "https://a/1", cidade="Gotham")], base_padrao())
    assert corridas == [] and descartadas == 1
