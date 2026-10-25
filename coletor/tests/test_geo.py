from coletor.geo import base_padrao


def test_localiza_com_uf():
    m = base_padrao().localizar("sao jose dos campos", "SP")
    assert m and m.nome == "São José dos Campos" and m.uf == "SP"


def test_nome_ambiguo_sem_uf_nao_localiza():
    # Existe "Bom Jesus" em vários estados.
    assert base_padrao().localizar("Bom Jesus", None) is None


def test_nome_unico_sem_uf():
    assert base_padrao().localizar("Jundiaí", None).uf == "SP"


def test_cidade_inexistente():
    assert base_padrao().localizar("Gotham", "SP") is None
