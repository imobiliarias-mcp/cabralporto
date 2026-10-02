"""Central rental research MCP interface and client."""

from cabralporto_research.collaborators import RentalNetworkGateway, RentalParserSuite
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType, SortOrder
from cabralporto_research.domain.listing import RentalListingCollection
from cabralporto_research.domain.metadata import FacetCollection
from cabralporto_research.domain.property import PropertyDetail


class CabralPortoRentalClient:
    """Central rental research client serving as the project's MCP interface."""

    def __init__(
        self,
        gateway: RentalNetworkGateway | None = None,
        parsers: RentalParserSuite | None = None,
    ) -> None:
        """Initialize client with gateway and parser suite collaborators."""
        self._gateway = gateway or RentalNetworkGateway()
        self._parsers = parsers or RentalParserSuite(
            public_base_url=self._gateway.public_site_base_url()
        )

    def search(self, criteria: SearchCriteria) -> RentalListingCollection:
        """Execute search query and return parsed collection of listings."""
        resp = self._gateway.fetch_search(criteria)
        parser = self._parsers.search_parser
        return parser.parse(resp.json_data)

    def search_rentals(
        self, city_slug: str = "timoteo-mg", property_type: PropertyType = PropertyType.IMOVEIS,
        bedrooms: int | None = None, min_bedrooms: bool = True, suites: int | None = None,
        garages: int | None = None, min_price: int | None = None, max_price: int | None = None,
        page: int = 1, limit: int = 21, sort: SortOrder = SortOrder.RECENT,
    ) -> RentalListingCollection:
        """Convenience method for executing rental searches with standard filters."""
        args = (city_slug, property_type, bedrooms, min_bedrooms, suites, garages, min_price, max_price, page, limit, sort)
        return self.search(SearchCriteria.create_rental(*args))

    def get_details(self, property_id_or_reference: str) -> PropertyDetail:
        """Retrieve full details for a specific property by ID or reference code."""
        resp = self._gateway.fetch_detail(property_id_or_reference)
        parser = self._parsers.detail_parser
        return parser.parse(resp.json_data)

    def get_facets(self) -> FacetCollection:
        """Fetch consolidated metadata and filter facets."""
        facets_map = self._gateway.fetch_facets()
        s_data = facets_map["states"].json_data
        n_data = facets_map["neighborhoods"].json_data
        t_data = facets_map["types"].json_data
        return self._parsers.metadata_parser.parse_facets(s_data, n_data, t_data)

