"""Public property URL contract tests for both Cabral Porto implementations."""

from types import SimpleNamespace

import pytest

from cabralporto_research.client import CabralPortoRentalClient
from cabralporto_research.collaborators import RentalNetworkGateway
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.listing import (
    ListingLocation,
    ListingSpecs,
    RentalListingCollection,
    RentalListingSummary,
)
from cabralporto_research.infrastructure.http_client import HttpResponse
from cabralporto_research.infrastructure.url_builder import UrlBuilder
from cabralporto_research.parsers.public_url import PublicPropertyUrlError
from cabralporto_research.parsers.search_parser import SearchResponseParser
from scripts import verify_research
from scripts.client.configuration import CabralPortoConfiguration
from scripts.client.parsers import ResponseParser
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import (
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingResources,
    ListingValuation,
    RentalListing,
)
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.mcp.tools import CabralPortoMcpAdapter
from scripts.providers.cabralporto import CabralPortoRentalProvider
from scripts.run_search import display_results

PUBLIC_BASE = "https://cabralportoimoveis.com.br"
CUSTOM_BASE = "https://listings.example.test"


@pytest.mark.parametrize(
    ("details", "expected_media_url"),
    [
        (ListingDetails("Eldorado, Timóteo", media_url="keyword.jpg"), "keyword.jpg"),
        (ListingDetails("Eldorado, Timóteo", "positional.jpg"), "positional.jpg"),
        (
            ListingDetails(
                "Eldorado, Timóteo",
                resources=ListingResources(media_url="composed.jpg", property_url="https://example.test/property"),
            ),
            "composed.jpg",
        ),
    ],
    ids=("legacy-keyword", "legacy-positional", "composed-resources"),
)
def test_listing_details_exposes_legacy_media_url(details, expected_media_url: str) -> None:
    """Expose media URL through both legacy and composed details construction."""
    assert details.media_url == expected_media_url


@pytest.mark.parametrize(
    ("raw_url", "expected_url"),
    [
        (
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
        ),
        (
            "/imovel/apartamento-eldorado/422?property_id=608",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422?property_id=608",
        ),
        (
            "imovel/apartamento-eldorado/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
        ),
        (
            "apartamento-para-alugar-no-bairro-eldorado-em-timoteo-mg/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-para-alugar-no-bairro-eldorado-em-timoteo-mg/422",
        ),
        (
            "//cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
        ),
        (
            "/imovel/apartamento-eldorado?id=608",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado?id=608",
        ),
    ],
)
def test_core_parser_serializes_absolute_property_url(raw_url: str, expected_url: str) -> None:
    """Normalize public card URL forms and preserve the legacy URL field."""
    payload = {"data": [{"id": "api-uuid", "reference": "422", "url": raw_url}]}

    listing = SearchResponseParser().parse(payload)[0]
    serialized = listing.to_dictionary()

    assert listing.detail_url == expected_url
    assert serialized["url"] == expected_url
    assert serialized["detail_url"] == expected_url


def test_script_and_core_parsers_normalize_bare_slug_consistently() -> None:
    """Place observed bare card slugs under the same property route."""
    bare_slug = "apartamento-eldorado/422"
    core_listing = SearchResponseParser().parse(
        {"data": [{"id": "api-uuid", "reference": "422", "url": bare_slug}]}
    )[0]
    script_result = ResponseParser().parse_search_json(
        {"data": [{"id": "api-uuid", "reference": "422", "url": bare_slug}]}
    )
    expected_url = f"{PUBLIC_BASE}/imovel/{bare_slug}"

    assert core_listing.detail_url == expected_url
    assert script_result.to_dictionary()["listings"][0]["url"] == expected_url


def test_core_parser_rejects_malformed_url_with_property_context() -> None:
    """Convert malformed URL parsing errors into contextual domain failures."""
    parser = SearchResponseParser()

    with pytest.raises(PublicPropertyUrlError, match="422"):
        parser.parse({"data": [{"id": "api-uuid", "reference": "422", "url": "http://[broken"}]})


def test_core_parser_rejects_missing_or_invalid_public_urls() -> None:
    """Never fabricate a public URL from an internal API identifier or reference."""
    parser = SearchResponseParser()

    invalid_urls = (
        "javascript:alert(1)",
        "https://api-sites.tecimob.com.br/api/properties/422",
        "https://cabralportoimoveis.com.br/images/property.jpg",
        "https://cabralportoimoveis.com.br/alugar/imoveis/timoteo-mg",
    )
    with pytest.raises(ValueError, match="422"):
        parser.parse({"data": [{"id": "api-uuid", "reference": "422"}]})
    for invalid_url in invalid_urls:
        with pytest.raises(ValueError, match="422"):
            parser.parse({"data": [{"id": "api-uuid", "reference": "422", "url": invalid_url}]})


def test_core_client_uses_public_base_from_url_builder_without_extra_requests() -> None:
    """Carry configured public-site origin through the client parser boundary."""
    transport = CoreSearchTransport(
        {"data": [{"id": "api-uuid", "reference": "422", "url": "/imovel/apartamento/422"}]}
    )
    gateway = RentalNetworkGateway(
        http_client=transport,
        url_builder=UrlBuilder(site_base=CUSTOM_BASE),
    )
    client = CabralPortoRentalClient(gateway=gateway)

    result = client.search(SearchCriteria.create_rental(city_slug="timoteo-mg"))

    assert result[0].to_dictionary()["url"] == f"{CUSTOM_BASE}/imovel/apartamento/422"
    assert transport.call_count == 1


@pytest.mark.parametrize(
    ("raw_url", "expected_url"),
    [
        (
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
        ),
        (
            "/imovel/apartamento-eldorado/422?property_id=608",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422?property_id=608",
        ),
        (
            "//cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
        ),
        (
            "/imovel/apartamento-eldorado?id=608",
            "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado?id=608",
        ),
    ],
)
def test_scripts_parser_preserves_public_url_in_mcp_dictionary(raw_url: str, expected_url: str) -> None:
    """Keep search URL in the adapter dictionary while preserving other fields."""
    result = ResponseParser().parse_search_json(
        {
            "data": [
                {
                    "id": "api-uuid",
                    "reference": "422",
                    "title_formatted": "Apartamento Eldorado",
                    "price": "R$1.400,00",
                    "url": raw_url,
                }
            ],
            "meta": {"pagination": {"total": 1}},
        }
    )

    serialized = CabralPortoMcpAdapter(FixedSearchProvider(result)).search_rentals()
    listing = serialized["listings"][0]

    assert listing["url"] == expected_url
    assert listing["code"] == "422"
    assert listing["rental_price"] == 1400.0
    assert listing["media_url"] == ""
    assert serialized["total_count"] == 1


@pytest.mark.parametrize("property_url", ["", "/imovel/apartamento/422", "ftp://example.test/imovel/422"])
def test_scripts_listing_serializer_rejects_unresolved_public_url(property_url: str) -> None:
    """Reject missing or nonabsolute public URLs from manually built listings."""
    resources = ListingDetails(location_summary="Eldorado, Timóteo", media_url="legacy-image.jpg")
    if property_url:
        resources = ListingDetails(
            location_summary="Eldorado, Timóteo",
            media_url="legacy-image.jpg",
            property_url=property_url,
        )
    listing = RentalListing(
        core=ListingCore(
            identity=ListingIdentity(code=PropertyCode("422"), title="Apartamento"),
            valuation=ListingValuation(rental_price=ListingPrice(1400), property_type="Apartamento"),
        ),
        details=resources,
    )

    with pytest.raises(ValueError, match="422"):
        listing.to_dictionary()


def test_scripts_parser_rejects_non_property_destinations() -> None:
    """Reject Tecimob API, image, and documented search URLs as property links."""
    invalid_urls = (
        "https://api-sites.tecimob.com.br/api/properties/422",
        "https://cabralportoimoveis.com.br/images/property.jpg",
        "https://cabralportoimoveis.com.br/alugar/imoveis/timoteo-mg",
    )
    for invalid_url in invalid_urls:
        with pytest.raises(ValueError, match="422"):
            ResponseParser().parse_search_json(
                {"data": [{"id": "api-uuid", "reference": "422", "url": invalid_url}]}
            )


def test_scripts_provider_uses_configured_public_base_and_only_searches_once() -> None:
    """Pass configured portal origin to parser without detail requests."""
    config = CabralPortoConfiguration(base_url=CUSTOM_BASE)
    transport = ScriptSearchTransport(
        config.base_url,
        {"data": [{"id": "api-uuid", "reference": "422", "url": "/imovel/apartamento/422"}]},
    )
    provider = CabralPortoRentalProvider(
        transport=transport,
        query_builder=RentalQueryBuilder(configuration=config),
    )

    listing = next(iter(provider.search_rentals(RentalFilter()).listings()))

    assert listing.to_dictionary()["url"] == f"{CUSTOM_BASE}/imovel/apartamento/422"
    assert transport.call_count == 1


def test_cli_search_prints_public_property_link(capsys: pytest.CaptureFixture[str]) -> None:
    """Show the serialized public URL beside each search result."""
    result = ResponseParser().parse_search_json(
        {"data": [{"id": "uuid", "reference": "422", "url": "/imovel/apartamento/422"}]}
    )

    display_results(result)

    assert f"Link: {PUBLIC_BASE}/imovel/apartamento/422" in capsys.readouterr().out


def test_verification_runner_prints_public_property_link(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """Show public property URLs in the existing core verification searches."""
    location = ListingLocation(neighborhood="Eldorado", city="Timóteo", formatted="Eldorado - Timóteo/MG")
    listing = RentalListingSummary(
        property_id="api-uuid",
        reference="422",
        title="Apartamento Eldorado",
        price="R$1.400,00",
        transaction="ALUGUEL",
        location=location,
        specs=ListingSpecs(),
        thumbnail_url=None,
        detail_url=f"{PUBLIC_BASE}/imovel/apartamento/422",
    )
    results = RentalListingCollection(items=(listing,))
    detail = SimpleNamespace(
        title="Apartamento Eldorado",
        reference="422",
        pricing=SimpleNamespace(price="R$1.400,00", total_price="R$1.400,00", condominium_price="R$0,00"),
        location=SimpleNamespace(formatted="Eldorado - Timóteo/MG"),
        specs=SimpleNamespace(bedrooms=2, bathrooms=1, garages=1),
        photos=(),
    )

    class StubClient:
        def search(self, _criteria):
            return results

        def search_rentals(self, **_criteria):
            return results

        def get_details(self, _code):
            return detail

        def get_facets(self):
            return SimpleNamespace(cities=(), neighborhoods=(), types=())

    monkeypatch.setattr(verify_research, "CabralPortoRentalClient", StubClient)
    verify_research.main()

    assert capsys.readouterr().out.count(f"Link: {PUBLIC_BASE}/imovel/apartamento/422") == 2


class CoreSearchTransport:
    """Stub core HTTP client that counts the original search request."""

    def __init__(self, json_data: dict) -> None:
        self._json_data = json_data
        self.call_count = 0

    def get(self, url: str, params: dict | None = None) -> HttpResponse:
        self.call_count += 1
        return HttpResponse(200, "{}", self._json_data, final_url=url)


class ScriptSearchTransport:
    """Stub adapter transport exposing the configured public base URL."""

    def __init__(self, public_base_url: str, json_data: dict) -> None:
        self._public_base_url = public_base_url
        self._json_data = json_data
        self.call_count = 0

    def get_json(self, url: str, params: dict | None = None) -> dict:
        self.call_count += 1
        return self._json_data

    def public_base_url(self) -> str:
        return self._public_base_url


class FixedSearchProvider:
    """Supply a parsed result to the existing MCP adapter without network calls."""

    def __init__(self, result) -> None:
        self._result = result

    def search_rentals(self, _search_filter):
        return self._result
