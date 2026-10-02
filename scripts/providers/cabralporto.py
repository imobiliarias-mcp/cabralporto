"""Cabral Porto Imóveis rental search provider implementation."""

import httpx

from scripts.client.configuration import CabralPortoConfiguration
from scripts.client.http_transport import CabralPortoHttpTransport
from scripts.client.parsers import ResponseParser
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol


class CabralPortoRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Cabral Porto Imóveis."""

    def __init__(
        self,
        transport: CabralPortoHttpTransport,
        query_builder: RentalQueryBuilder,
    ) -> None:
        """Initialize provider with transport and query builder collaborators."""
        self._transport = transport
        self._builder = query_builder

    @classmethod
    def create_default(cls) -> "CabralPortoRentalProvider":
        """Factory method constructing provider with default configurations."""
        config = CabralPortoConfiguration()
        client = httpx.Client(timeout=20.0, follow_redirects=True)
        transport = CabralPortoHttpTransport(configuration=config, http_client=client)
        builder = RentalQueryBuilder(configuration=config)
        return cls(transport=transport, query_builder=builder)

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "cabralporto"

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings using criteria."""
        search_url = self._builder.build_api_search_url()
        params = self._builder.build_api_parameters(search_filter)
        json_data = self._transport.get_json(search_url, params=params)
        parser = ResponseParser(public_base_url=self._transport.public_base_url())
        return parser.parse_search_json(json_data)

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details for a single property by code."""
        detail_url = self._builder.build_api_detail_url(code)
        json_data = self._transport.get_json(detail_url)
        parser = ResponseParser(public_base_url=self._transport.public_base_url())
        return parser.parse_detail_json(json_data)

    def get_facets(self) -> FacetCollection:
        """Retrieve available cities and neighborhoods for filtering."""
        states_url = f"{self._builder._config.api_base_url}/filters/states"
        neigh_url = f"{self._builder._config.api_base_url}/filters/neighborhoods"
        states_json = self._transport.get_json(states_url, params={"sort": "acronym"})
        neigh_json = self._transport.get_json(neigh_url, params={"sort": "slug"})
        parser = ResponseParser()
        return parser.parse_facets_json(states_json=states_json, neighborhoods_json=neigh_json)
