"""Unit tests for URL and query parameters builder."""

from urllib.parse import parse_qs, urlparse
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType, SortOrder, TransactionType
from cabralporto_research.infrastructure.url_builder import UrlBuilder


def test_build_api_search_url() -> None:
    """Verify API search URL endpoint."""
    builder = UrlBuilder()
    url = builder.build_api_search_url()
    assert url == "https://api-sites.tecimob.com.br/api/properties"


def test_build_target_prompt_api_params() -> None:
    """Verify parameters for target prompt query."""
    builder = UrlBuilder()
    criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.IMOVEIS,
        bedrooms=2,
        min_bedrooms=True,
        page=1,
        limit=21,
        sort=SortOrder.RECENT,
    )
    params = builder.build_api_search_params(criteria)
    assert params["custom_query"] == "card"
    assert params["sort"] == "-created_at,id"
    assert params["offset"] == "1"
    assert params["limit"] == "21"
    assert params["filter[transaction]"] == "2"
    assert params["filter[by_neighborhood_or_city_slug]"] == "timoteo-mg"
    assert params["filter[by_room_greater_equals][bedroom]"] == "2"


def test_build_api_params_with_all_filters() -> None:
    """Verify parameters when price, area, suites, and garages are added."""
    builder = UrlBuilder()
    criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=3,
        suites=1,
        garages=2,
        min_price=1200,
        max_price=3500,
        page=2,
        limit=10,
    )
    params = builder.build_api_search_params(criteria)
    assert params["filter[by_type_or_subtype_slug]"] == "apartamento"
    assert params["filter[by_room_greater_equals][bedroom]"] == "3"
    assert params["filter[by_room_greater_equals][suite]"] == "1"
    assert params["filter[by_room_greater_equals][garage]"] == "2"
    assert params["filter[by_higher_than_price]"] == "1200"
    assert params["filter[by_lower_than_price]"] == "3500"
    assert params["offset"] == "2"
    assert params["limit"] == "10"


def test_build_api_detail_and_filter_urls() -> None:
    """Verify detail and facet filter URL generation."""
    builder = UrlBuilder()
    detail_url = builder.build_api_detail_url("422")
    assert detail_url == "https://api-sites.tecimob.com.br/api/properties/422"

    filter_url = builder.build_api_filter_url("filters/states")
    assert filter_url == "https://api-sites.tecimob.com.br/api/filters/states"


def test_build_canonical_website_target_url() -> None:
    """Verify reproduction of the exact target prompt website URL."""
    builder = UrlBuilder()
    criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.IMOVEIS,
        bedrooms=2,
        page=1,
        limit=21,
        sort=SortOrder.RECENT,
    )
    web_url = builder.build_canonical_website_url(criteria)
    parsed = urlparse(web_url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "cabralportoimoveis.com.br"
    assert parsed.path == "/alugar/imoveis/timoteo-mg"

    query_params = parse_qs(parsed.query)
    assert query_params["typeArea"] == ["total_area"]
    assert query_params["floorComparision"] == ["equals"]
    assert query_params["sort"] == ["-created_at,id"]
    assert query_params["offset"] == ["1"]
    assert query_params["limit"] == ["21"]
    assert query_params["bedrooms"] == ["2"]
