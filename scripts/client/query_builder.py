"""Query builder translating RentalFilter to canonical portal routes and API parameters."""

from urllib.parse import urlencode
from scripts.client.configuration import CabralPortoConfiguration
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode


class RentalQueryBuilder:
    """Builds search request URLs and parameter dictionaries from RentalFilter."""

    def __init__(self, configuration: CabralPortoConfiguration | None = None) -> None:
        """Initialize query builder with portal configuration."""
        self._config = configuration or CabralPortoConfiguration()

    def build_api_search_url(self) -> str:
        """Construct full URL to Tecimob properties endpoint."""
        return f"{self._config.api_base_url}/properties"

    def build_api_detail_url(self, code: PropertyCode) -> str:
        """Construct full URL to Tecimob property detail endpoint."""
        return f"{self._config.api_base_url}/properties/{code.value()}"

    def build_api_parameters(self, search_filter: RentalFilter) -> dict[str, str]:
        """Convert domain filter into Tecimob query parameter dictionary."""
        city_slug = self._resolve_city_slug(search_filter)
        page = search_filter.constraints.pagination.page_number
        params = self._base_search_parameters(city_slug, page)
        self._apply_bedrooms(params, search_filter)
        self._apply_price(params, search_filter)
        self._apply_property_type(params, search_filter)
        return params

    def _base_search_parameters(self, city_slug: str, page: int) -> dict[str, str]:
        """Construct base pagination and location parameters."""
        return {
            "custom_query": "card",
            "sort": "-created_at,id",
            "offset": str(page),
            "limit": "21",
            "filter[transaction]": "2",
            "filter[by_neighborhood_or_city_slug]": city_slug,
        }


    def _resolve_city_slug(self, search_filter: RentalFilter) -> str:
        """Map filter city to URL slug identifier."""
        raw_city = search_filter.criteria.location.city.strip().lower()
        if not raw_city:
            return "timoteo-mg"
        if not raw_city.endswith("-mg"):
            raw_city = f"{raw_city}-mg"
        cleaned = raw_city.replace("ó", "o").replace("é", "e").replace("á", "a")
        return cleaned.replace(" ", "-")

    def _apply_bedrooms(self, params: dict[str, str], search_filter: RentalFilter) -> None:
        """Encode bedroom count filter."""
        count = search_filter.criteria.specifications.minimum_bedrooms
        if count <= 0:
            return
        params["filter[by_room_greater_equals][bedroom]"] = str(count)

    def _apply_price(self, params: dict[str, str], search_filter: RentalFilter) -> None:
        """Encode price constraints."""
        max_price = search_filter.constraints.price_range.maximum_price.value()
        min_price = search_filter.constraints.price_range.minimum_price.value()
        if max_price > 0.0:
            params["filter[by_lower_than_price]"] = str(int(max_price))
        if min_price > 0.0:
            params["filter[by_higher_than_price]"] = str(int(min_price))

    def _apply_property_type(self, params: dict[str, str], search_filter: RentalFilter) -> None:
        """Encode property type constraint."""
        raw_type = search_filter.criteria.specifications.property_type.strip().lower()
        if raw_type and raw_type != "imoveis":
            params["filter[by_type_or_subtype_slug]"] = raw_type

    def build_canonical_website_url(self, search_filter: RentalFilter) -> str:
        """Construct canonical website search URL matching site routing conventions."""
        city_slug = self._resolve_city_slug(search_filter)
        raw_type = search_filter.criteria.specifications.property_type.strip().lower() or "imoveis"
        query_params = {
            "typeArea": "total_area",
            "floorComparision": "equals",
            "sort": "-created_at,id",
            "offset": str(search_filter.constraints.pagination.page_number),
            "limit": "21",
        }
        if search_filter.criteria.specifications.minimum_bedrooms > 0:
            query_params["bedrooms"] = str(search_filter.criteria.specifications.minimum_bedrooms)
        query_string = urlencode(query_params)
        return f"{self._config.base_url}/alugar/{raw_type}/{city_slug}?{query_string}"
