"""Metadata entities for cities, neighborhoods, and facet collections."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class City:
    """Represents municipality metadata."""

    id: str
    name: str
    state_acronym: str = "MG"


@dataclass(frozen=True)
class Neighborhood:
    """Represents neighborhood metadata."""

    id: str
    name: str


@dataclass(frozen=True)
class PropertyTypeItem:
    """Represents property type option."""

    id: str
    title: str
    symbol: str = "house"


@dataclass(frozen=True)
class FacetCollection:
    """First-class collection representing available search facet values."""

    cities: tuple[City, ...] = field(default_factory=tuple)
    neighborhoods: tuple[Neighborhood, ...] = field(default_factory=tuple)
    types: tuple[PropertyTypeItem, ...] = field(default_factory=tuple)

    def find_city_by_slug(self, slug: str) -> City | None:
        """Find city by its slug identifier."""
        for city in self.cities:
            if city.id.lower() == slug.lower():
                return city
        return None

    def find_neighborhood_by_name(self, name: str) -> Neighborhood | None:
        """Find neighborhood by name case-insensitively."""
        normalized = name.lower()
        for neighborhood in self.neighborhoods:
            if neighborhood.name.lower() == normalized:
                return neighborhood
        return None

    def to_dictionary(self) -> dict:
        """Serialize facet collection to dictionary."""
        return {
            "cities": [{"id": c.id, "name": c.name, "state": c.state_acronym} for c in self.cities],
            "neighborhoods": [{"id": n.id, "name": n.name} for n in self.neighborhoods],
            "types": [{"id": t.id, "title": t.title, "symbol": t.symbol} for t in self.types],
        }
