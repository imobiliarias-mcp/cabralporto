"""Network gateway and parser suite collaborators for rental research client."""

from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
    PropertyNotFoundError,
)
from cabralporto_research.infrastructure.url_builder import UrlBuilder
from cabralporto_research.parsers.detail_parser import PropertyDetailParser
from cabralporto_research.parsers.metadata_parser import MetadataParser
from cabralporto_research.parsers.search_parser import SearchResponseParser


class RentalNetworkGateway:
    """Dispatches HTTP requests for rental searches, details, and metadata."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        url_builder: UrlBuilder | None = None,
    ) -> None:
        """Initialize gateway with network transport and URL builder."""
        self._http = http_client or HttpxHttpClient()
        self._builder = url_builder or UrlBuilder()

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Fetch search results page for given criteria."""
        url = self._builder.build_api_search_url()
        params = self._builder.build_api_search_params(criteria)
        return self._http.get(url, params=params)

    def fetch_detail(self, property_id_or_ref: str) -> HttpResponse:
        """Fetch detail page for a given property ID or reference code."""
        url = self._builder.build_api_detail_url(property_id_or_ref)
        resp = self._http.get(url)
        self._validate_property_response(resp, property_id_or_ref)
        return resp

    def fetch_facets(self) -> dict[str, HttpResponse]:
        """Fetch supporting filter metadata responses."""
        states_url = self._builder.build_api_filter_url("filters/states")
        neigh_url = self._builder.build_api_filter_url("filters/neighborhoods")
        types_url = self._builder.build_api_filter_url("filters/types")

        return {
            "states": self._http.get(states_url, params={"sort": "acronym"}),
            "neighborhoods": self._http.get(neigh_url, params={"sort": "slug"}),
            "types": self._http.get(types_url, params={"sort": "order", "filter[having_properties]": "true"}),
        }

    def _validate_property_response(self, resp: HttpResponse, property_id: str) -> None:
        """Validate response status code for property detail requests."""
        if resp.status_code in (404, 422):
            raise PropertyNotFoundError(f"Property with identifier '{property_id}' was not found.")


class ListingParserBundle:
    """Aggregates search and metadata parsers."""

    def __init__(self, search_parser: SearchResponseParser | None = None) -> None:
        """Initialize search and metadata parsers."""
        self._search = search_parser or SearchResponseParser()
        self._metadata = MetadataParser()

    @property
    def search_parser(self) -> SearchResponseParser:
        """Return search parser."""
        return self._search

    @property
    def metadata_parser(self) -> MetadataParser:
        """Return metadata parser."""
        return self._metadata


class DetailParserBundle:
    """Aggregates property detail parser."""

    def __init__(self, detail_parser: PropertyDetailParser | None = None) -> None:
        """Initialize detail parser."""
        self._detail = detail_parser or PropertyDetailParser()

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser."""
        return self._detail


class RentalParserSuite:
    """Composite suite containing listing and detail parser bundles."""

    def __init__(
        self,
        listing_bundle: ListingParserBundle | None = None,
        detail_bundle: DetailParserBundle | None = None,
    ) -> None:
        """Initialize suite with listing and detail bundles."""
        self._listing = listing_bundle or ListingParserBundle()
        self._detail = detail_bundle or DetailParserBundle()

    @property
    def search_parser(self) -> SearchResponseParser:
        """Return search parser."""
        return self._listing.search_parser

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser."""
        return self._detail.detail_parser

    @property
    def metadata_parser(self) -> MetadataParser:
        """Return metadata parser."""
        return self._listing.metadata_parser
