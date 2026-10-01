"""Parser for supporting metadata and filter facet responses."""

from typing import Any
from cabralporto_research.domain.metadata import City, FacetCollection, Neighborhood, PropertyTypeItem


class MetadataParser:
    """Parses filter facet endpoints into domain FacetCollection."""

    def parse_facets(
        self,
        states_data: dict[str, Any] | None = None,
        neighborhoods_data: dict[str, Any] | None = None,
        types_data: dict[str, Any] | None = None,
    ) -> FacetCollection:
        """Parse raw responses from filter endpoints into consolidated FacetCollection."""
        c = self._parse_cities(states_data)
        n = self._parse_neighborhoods(neighborhoods_data)
        t = self._parse_types(types_data)
        return FacetCollection(cities=tuple(c), neighborhoods=tuple(n), types=tuple(t))

    def _parse_cities(self, states_data: dict[str, Any] | None) -> list[City]:
        """Extract cities nested inside states list."""
        if not states_data or not isinstance(states_data, dict):
            return []
        items = states_data.get("data", [])
        if not isinstance(items, list):
            return []
        cities: list[City] = []
        for state_obj in items:
            if isinstance(state_obj, dict):
                cities.extend(self._extract_state_cities(state_obj))
        return cities

    def _extract_state_cities(self, state: dict[str, Any]) -> list[City]:
        """Extract cities for a specific state dictionary."""
        acr = state.get("acronym", "MG")
        raw_c = state.get("cities", [])
        if not isinstance(raw_c, list):
            return []
        return [
            City(id=str(c["id"]), name=str(c["name"]), state_acronym=acr)
            for c in raw_c
            if isinstance(c, dict) and c.get("id") and c.get("name")
        ]

    def _parse_neighborhoods(self, data: dict[str, Any] | None) -> list[Neighborhood]:
        """Extract neighborhood entities from neighborhoods endpoint."""
        if not data or not isinstance(data, dict):
            return []
        items = data.get("data", [])
        if not isinstance(items, list):
            return []
        return [
            Neighborhood(id=str(it["id"]), name=str(it["name"]))
            for it in items
            if isinstance(it, dict) and it.get("id") and it.get("name")
        ]

    def _parse_types(self, data: dict[str, Any] | None) -> list[PropertyTypeItem]:
        """Extract property types from types endpoint."""
        if not data or not isinstance(data, dict):
            return []
        items = data.get("data", [])
        if not isinstance(items, list):
            return []
        return [
            PropertyTypeItem(id=str(it["id"]), title=str(it["title"]), symbol=str(it.get("symbol", "house")))
            for it in items
            if isinstance(it, dict) and it.get("id") and it.get("title")
        ]
