import hashlib
from dataclasses import asdict, dataclass, field
from datetime import date


@dataclass
class CorridaBruta:
    """Corrida como extraída de uma fonte, antes de normalizar cidade/coordenadas."""

    nome: str
    data: date
    url: str
    fonte: str
    cidade: str | None = None
    uf: str | None = None
    distancias_km: list[float] = field(default_factory=list)
    preco_min: float | None = None


@dataclass
class Link:
    fonte: str
    url: str


@dataclass
class Corrida:
    id: str
    nome: str
    data: str  # ISO 8601 (AAAA-MM-DD)
    cidade: str
    uf: str
    codigo_ibge: int
    lat: float
    lon: float
    distancias_km: list[float]
    preco_min: float | None
    links: list[Link]

    @staticmethod
    def gerar_id(nome: str, data: str, codigo_ibge: int) -> str:
        chave = f"{nome.lower()}|{data}|{codigo_ibge}"
        return hashlib.sha1(chave.encode()).hexdigest()[:12]

    def para_dict(self) -> dict:
        return asdict(self)
