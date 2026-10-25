import json
from datetime import date

from coletor import cache
from coletor.dedup import consolidar
from coletor.exportar import exportar
from coletor.geo import base_padrao
from coletor.modelo import CorridaBruta


def test_exporta_por_uf_e_remove_passadas_e_ufs_vazias(tmp_path):
    (tmp_path / "corridas").mkdir()
    (tmp_path / "corridas" / "AM.json").write_text("[]")  # UF de uma execução antiga
    brutas = [
        CorridaBruta("Futura SP", date(2099, 1, 1), "https://a/1", "a", "Campinas", "SP", [5.0]),
        CorridaBruta("Futura RJ", date(2099, 1, 1), "https://a/2", "a", "Niterói", "RJ", [10.0]),
        CorridaBruta("Passada", date(2000, 1, 1), "https://a/3", "a", "Campinas", "SP", [5.0]),
    ]
    corridas, _ = consolidar(brutas, base_padrao())
    indice = exportar(corridas, {"a": {"ok": True}}, destino=tmp_path)

    assert indice["total"] == 2 and indice["por_uf"] == {"RJ": 1, "SP": 1}
    assert sorted(p.name for p in (tmp_path / "corridas").iterdir()) == ["RJ.json", "SP.json"]
    sp = json.loads((tmp_path / "corridas" / "SP.json").read_text(encoding="utf-8"))
    assert sp[0]["nome"] == "Futura SP" and sp[0]["links"] == [{"fonte": "a", "url": "https://a/1"}]
    assert (tmp_path / "municipios.json").exists() and (tmp_path / "estados.json").exists()


def test_cache_ida_e_volta(tmp_path):
    original = [CorridaBruta("X", date(2099, 5, 1), "https://a/1", "a", "Campinas", "SP", [5.0], 10.0)]
    cache.salvar("a", original, pasta=tmp_path)
    carregadas, coletado_em = cache.carregar("a", pasta=tmp_path)
    assert carregadas == original and coletado_em
    assert cache.carregar("inexistente", pasta=tmp_path) == ([], None)
