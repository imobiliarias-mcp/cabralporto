"""Live integration tests against Cabral Porto Imóveis portal and Tecimob API."""

import pytest
from cabralporto_research.client import CabralPortoRentalClient
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType, SortOrder
from cabralporto_research.infrastructure.http_client import PropertyNotFoundError


@pytest.fixture
def client() -> CabralPortoRentalClient:
    """Fixture providing initialized live client."""
    return CabralPortoRentalClient()


def test_live_target_prompt_url_search(client: CabralPortoRentalClient) -> None:
    """Verify live search matching the exact target prompt URL parameters.

    Target URL:
    https://cabralportoimoveis.com.br/alugar/imoveis/timoteo-mg?typeArea=total_area&floorComparision=equals&sort=-created_at%2Cid&offset=1&limit=21&bedrooms=2
    """
    criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.IMOVEIS,
        bedrooms=2,
        min_bedrooms=True,
        page=1,
        limit=21,
        sort=SortOrder.RECENT,
    )
    result = client.search(criteria)
    assert result.total_count >= 3
    assert len(result) >= 3

    references = [item.reference for item in result]
    assert "422" in references

    # Verify property 422 specs
    prop_422 = next(item for item in result if item.reference == "422")
    assert prop_422.specs.bedrooms == 2
    assert "Eldorado" in prop_422.location.neighborhood
    assert "1.400" in prop_422.price


def test_live_all_rentals_timoteo(client: CabralPortoRentalClient) -> None:
    """Verify live search for all rental properties in Timóteo."""
    result = client.search_rentals(city_slug="timoteo-mg", page=1, limit=21)
    assert result.total_count >= 7
    assert len(result) >= 7


def test_live_property_detail(client: CabralPortoRentalClient) -> None:
    """Verify live retrieval of full details for property 422."""
    detail = client.get_details("422")
    assert detail.reference == "422"
    assert "Apartamento" in detail.title
    assert "1.400" in detail.pricing.price
    assert detail.pricing.condominium_price == "R$220,00"
    assert detail.specs.bedrooms == 2
    assert detail.specs.bathrooms == 1
    assert detail.specs.garages == 1
    assert len(detail.photos) == 10
    assert detail.photos[0].large_url.startswith("https://imagens.tecimob.com.br")


def test_live_property_not_found(client: CabralPortoRentalClient) -> None:
    """Verify live client raises PropertyNotFoundError for non-existent property."""
    with pytest.raises(PropertyNotFoundError):
        client.get_details("999999")


def test_live_facets(client: CabralPortoRentalClient) -> None:
    """Verify live retrieval of cities, neighborhoods, and types facets."""
    facets = client.get_facets()
    assert len(facets.cities) >= 8
    assert len(facets.neighborhoods) >= 40
    assert len(facets.types) >= 10

    timoteo = facets.find_city_by_slug("timoteo-mg")
    assert timoteo is not None
    assert timoteo.name == "Timóteo"
