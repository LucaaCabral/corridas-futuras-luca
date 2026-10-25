from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_html():
    return lambda nome: (FIXTURES / nome).read_text(encoding="utf-8")
