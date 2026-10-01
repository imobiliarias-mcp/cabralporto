"""Canonical URL and API query parameter constructor."""

from urllib.parse import urlencode
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType


class UrlBuilder:
    """Constructs API endpoint URLs and query parameter dictionaries."""

    API_BASE = "https://api-sites.tecimob.com.br/api"
    SITE_BASE = "https://cabralportoimoveis.com.br"

    def __init__(self, api_base: str = API_BASE, site_base: str = SITE_BASE) -> None:
        """Initialize builder with API and website base URLs."""
        self._api_base = api_base.rstrip("/")
        self._site_base = site_base.rstrip("/")

    def build_api_search_url(self) -> str:
        """Return base API properties endpoint."""
        return f"{self._api_base}/properties"

    def build_api_search_params(self, criteria: SearchCriteria) -> dict[str, str]:
        """Convert domain search criteria into Tecimob query parameter dictionary."""
        params: dict[str, str] = {
            "custom_query": criteria.pagination.custom_query,
            "sort": criteria.pagination.sort.value,
            "offset": str(criteria.pagination.page.value),
            "limit": str(criteria.pagination.page.limit),
            "filter[transaction]": str(criteria.filters.transaction.to_tecimob_id()),
            "filter[by_neighborhood_or_city_slug]": criteria.filters.city_slug,
        }
        self._apply_type_filter(params, criteria)
        self._apply_room_filters(params, criteria)
        params.update(criteria.filters.price.query_parameters())
        params.update(criteria.filters.area.query_parameters())
        return params

    def _apply_type_filter(self, params: dict[str, str], criteria: SearchCriteria) -> None:
        """Apply property type and neighborhood filters."""
        if criteria.filters.property_type != PropertyType.IMOVEIS:
            params["filter[by_type_or_subtype_slug]"] = criteria.filters.property_type.value
        if criteria.filters.neighborhood_slug:
            params["filter[by_neighborhood_slug]"] = criteria.filters.neighborhood_slug

    def _apply_room_filters(self, params: dict[str, str], criteria: SearchCriteria) -> None:
        """Apply room constraint query parameters."""
        if criteria.filters.bedrooms:
            params.update(criteria.filters.bedrooms.query_parameters("bedroom"))
        if criteria.filters.suites:
            params.update(criteria.filters.suites.query_parameters("suite"))
        if criteria.filters.garages:
            params.update(criteria.filters.garages.query_parameters("garage"))

    def build_api_detail_url(self, property_id_or_reference: str) -> str:
        """Return endpoint URL for property detail retrieval."""
        cleaned_id = property_id_or_reference.strip()
        return f"{self._api_base}/properties/{cleaned_id}"

    def build_api_filter_url(self, endpoint_name: str) -> str:
        """Return endpoint URL for supporting filter facets."""
        cleaned_name = endpoint_name.strip().lstrip("/")
        return f"{self._api_base}/{cleaned_name}"

    def build_canonical_website_url(self, criteria: SearchCriteria) -> str:
        """Construct canonical website search URL matching site routing conventions."""
        tx = criteria.filters.transaction.value
        pt = criteria.filters.property_type.value
        city = criteria.filters.city_slug
        query_str = urlencode(self._build_canonical_query(criteria))
        return f"{self._site_base}/{tx}/{pt}/{city}?{query_str}"

    def _build_canonical_query(self, criteria: SearchCriteria) -> dict[str, str]:
        """Build dictionary of query parameters for frontend search URL."""
        query_params: dict[str, str] = {
            "typeArea": criteria.filters.area.area_type,
            "floorComparision": "equals",
            "sort": criteria.pagination.sort.value,
            "offset": str(criteria.pagination.page.value),
            "limit": str(criteria.pagination.page.limit),
        }
        if criteria.filters.bedrooms:
            query_params["bedrooms"] = str(criteria.filters.bedrooms.count)
        return query_params

