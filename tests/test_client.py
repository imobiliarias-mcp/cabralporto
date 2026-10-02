"""Unit tests for CabralPortoRentalClient with stubbed network transport."""

import pytest

from cabralporto_research.client import CabralPortoRentalClient
from cabralporto_research.collaborators import RentalNetworkGateway
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType
from cabralporto_research.infrastructure.http_client import (
    HttpResponse,
    PropertyNotFoundError,
)


class StubHttpClient:
    """Stub network client returning pre-configured responses."""

    def __init__(self) -> None:
        """Initialize stub."""
        self.last_url = ""
        self.last_params = None

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Return canned HTTP response depending on endpoint."""
        self.last_url = url
        self.last_params = params

        if "properties/999" in url:
            return HttpResponse(status_code=422, text='{"message": "Não encontrado."}', json_data={}, final_url=url)

        if "properties/422" in url:
            return HttpResponse(
                status_code=200,
                text="{}",
                json_data={
                    "data": {
                        "id": "uuid-422",
                        "reference": "422",
                        "title_formatted": "Apartamento em Eldorado",
                        "price": "R$1.400,00",
                        "transaction": "ALUGUEL",
                        "status": "Disponível",
                        "address": {"formatted": "Eldorado - Timóteo/MG"},
                        "rooms": {"bedroom": {"value": 2}},
                        "areas": {"built_area": {"value": "65", "measure": "m²"}},
                        "description": "Belo apartamento",
                        "images_extra": [],
                    }
                },
                final_url=url,
            )

        if "filters/states" in url:
            return HttpResponse(
                status_code=200,
                text="{}",
                json_data={"data": [{"id": "MG", "acronym": "MG", "cities": [{"id": "timoteo-mg", "name": "Timóteo"}]}]},
                final_url=url,
            )

        if "filters/neighborhoods" in url:
            return HttpResponse(
                status_code=200,
                text="{}",
                json_data={"data": [{"id": "timoteo-mg-eldorado", "name": "Eldorado"}]},
                final_url=url,
            )

        if "filters/types" in url:
            return HttpResponse(
                status_code=200,
                text="{}",
                json_data={"data": [{"id": "apartamento", "title": "Apartamento"}]},
                final_url=url,
            )

        # Default search response
        return HttpResponse(
            status_code=200,
            text="{}",
            json_data={
                "data": [
                    {
                        "id": "uuid-422",
                        "reference": "422",
                        "title_formatted": "Apartamento em Eldorado",
                        "price": "R$1.400,00",
                        "transaction": "ALUGUEL",
                        "url": "/imovel/apartamento-para-alugar-no-bairro-eldorado-em-timoteo-mg/422",
                        "address": {"formatted": "Eldorado - Timóteo/MG"},
                        "rooms": {"bedroom": {"value": 2}},
                    }
                ],
                "meta": {
                    "pagination": {
                        "total": 1,
                        "per_page": 21,
                        "current_page": 1,
                        "total_pages": 1,
                    }
                },
            },
            final_url=url,
        )


def test_client_search_with_stub() -> None:
    """Verify client search dispatches correct parameters and parses results."""
    stub_http = StubHttpClient()
    gateway = RentalNetworkGateway(http_client=stub_http)
    client = CabralPortoRentalClient(gateway=gateway)

    criteria = SearchCriteria.create_rental(city_slug="timoteo-mg", bedrooms=2)
    results = client.search(criteria)

    assert len(results) == 1
    assert results.total_count == 1
    assert results[0].reference == "422"
    assert stub_http.last_params["filter[by_room_greater_equals][bedroom]"] == "2"


def test_client_search_rentals_convenience() -> None:
    """Verify search_rentals convenience method."""
    stub_http = StubHttpClient()
    gateway = RentalNetworkGateway(http_client=stub_http)
    client = CabralPortoRentalClient(gateway=gateway)

    results = client.search_rentals(city_slug="timoteo-mg", property_type=PropertyType.APARTAMENTO, bedrooms=2)
    assert len(results) == 1
    assert results[0].reference == "422"


def test_client_get_details_success() -> None:
    """Verify client retrieves and parses property details."""
    stub_http = StubHttpClient()
    gateway = RentalNetworkGateway(http_client=stub_http)
    client = CabralPortoRentalClient(gateway=gateway)

    detail = client.get_details("422")
    assert detail.reference == "422"
    assert detail.pricing.price == "R$1.400,00"
    assert detail.specs.bedrooms == 2


def test_client_get_details_not_found() -> None:
    """Verify client raises PropertyNotFoundError on 422/404."""
    stub_http = StubHttpClient()
    gateway = RentalNetworkGateway(http_client=stub_http)
    client = CabralPortoRentalClient(gateway=gateway)

    with pytest.raises(PropertyNotFoundError):
        client.get_details("999")


def test_client_get_facets() -> None:
    """Verify client retrieves and parses search facets."""
    stub_http = StubHttpClient()
    gateway = RentalNetworkGateway(http_client=stub_http)
    client = CabralPortoRentalClient(gateway=gateway)

    facets = client.get_facets()
    assert len(facets.cities) == 1
    assert facets.cities[0].name == "Timóteo"
    assert len(facets.neighborhoods) == 1
    assert facets.neighborhoods[0].name == "Eldorado"
    assert len(facets.types) == 1
