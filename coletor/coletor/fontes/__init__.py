from .base import Cliente, Fonte
from .brasilquecorre import BrasilQueCorre
from .corridasbrasil import CorridasBrasil
from .minhasinscricoes import MinhasInscricoes
from .sympla import Sympla
from .ticketsports import TicketSports

FONTES: dict[str, type[Fonte]] = {
    f.nome: f for f in (TicketSports, MinhasInscricoes, BrasilQueCorre, CorridasBrasil, Sympla)
}

__all__ = ["FONTES", "Cliente", "Fonte"]
