from datetime import date

import pytest

from coletor.normalizar import (
    normalizar_texto, parse_data, parse_distancias, parse_preco, parse_uf, separar_cidade_uf,
)


@pytest.mark.parametrize("texto, esperado", [
    ("2026-11-15T07:00:00-03:00", date(2026, 11, 15)),
    ("15/11/2026", date(2026, 11, 15)),
    ("Domingo, 5.4.27", date(2027, 4, 5)),
    ("15 de novembro de 2026", date(2026, 11, 15)),
    ("15 NOV. 2026", date(2026, 11, 15)),
    ("3 de março de 2027", date(2027, 3, 3)),
    ("31/02/2026", None),
    ("em breve", None),
    (None, None),
])
def test_parse_data(texto, esperado):
    assert parse_data(texto) == esperado


@pytest.mark.parametrize("texto, esperado", [
    ("Corrida 5K e 10K", [5.0, 10.0]),
    ("Percursos de 21,1 km e 3km caminhada", [3.0, 21.1]),
    ("Meia Maratona do Rio", [21.1]),
    ("Maratona de São Paulo", [42.195]),
    ("Maratona e Meia Maratona", [21.1, 42.195]),
    ("Kids 0,2k", []),
    ("Sem distâncias", []),
])
def test_parse_distancias(texto, esperado):
    assert parse_distancias(texto) == esperado


@pytest.mark.parametrize("valor, esperado", [
    ("R$ 89,90", 89.9), ("R$ 1.250,00", 1250.0), ("R$ 1.250", 1250.0), ("12,5", 12.5),("119.90", 119.9), (150, 150.0), ("Grátis", None), (None, None),
])
def test_parse_preco(valor, esperado):
    assert parse_preco(valor) == esperado


def test_parse_uf():
    assert parse_uf("sp") == "SP"
    assert parse_uf("São Paulo") == "SP"
    assert parse_uf("Narnia") is None


@pytest.mark.parametrize("texto, esperado", [
    ("Campinas - SP", ("Campinas", "SP")),
    ("Campinas/SP", ("Campinas", "SP")),
    ("São José dos Campos, SP", ("São José dos Campos", "SP")),
    ("Campinas", ("Campinas", None)),
])
def test_separar_cidade_uf(texto, esperado):
    assert separar_cidade_uf(texto) == esperado


def test_normalizar_texto():
    assert normalizar_texto("  São  José-dos Campos! ") == "sao jose dos campos"
