"""Domain enumerations for Cabral Porto transactions and properties."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction purpose type."""

    ALUGAR = "alugar"
    COMPRAR = "comprar"

    def to_tecimob_id(self) -> int:
        """Return numeric transaction ID used by Tecimob API."""
        if self == TransactionType.ALUGAR:
            return 2
        return 1


class PropertyType(str, Enum):
    """Property type categories."""

    IMOVEIS = "imoveis"
    APARTAMENTO = "apartamento"
    CASA = "casa"
    COMERCIAL = "comercial"
    LOJA = "loja"
    SALA = "sala"
    FLAT = "flat"
    TERRENO = "terreno"
    PREDIO = "predio"
    GALPAO = "pavilhao-galpao"


class SortOrder(str, Enum):
    """Listing sort orders supported by Tecimob."""

    RECENT = "-created_at,id"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"
    DEFAULT = "-is_price_shown,by_calculated_price,id"
