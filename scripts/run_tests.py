#!/usr/bin/env python3
"""Automated verification suite validating domain models, query builders, and live provider."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.criteria import PriceRange, RentalFilter
from scripts.domain.exceptions import InvalidFilterException, InvalidPriceException
from scripts.domain.value_objects import GeoCoordinate, ListingPrice, PropertyCode
from scripts.mcp.tools import CabralPortoMcpAdapter
from scripts.providers.cabralporto import CabralPortoRentalProvider


def test_listing_price_validation() -> None:
    """Verify ListingPrice rejects negative amounts and formats BRL."""
    price = ListingPrice(1400.00)
    assert price.format_brl() == "R$ 1.400,00"
    assert not price.is_zero()
    try:
        ListingPrice(-50.0)
        assert False, "Should have raised InvalidPriceException"
    except InvalidPriceException:
        pass


def test_price_range_validation() -> None:
    """Verify PriceRange raises error when minimum exceeds maximum."""
    min_price = ListingPrice(3000.0)
    max_price = ListingPrice(1000.0)
    try:
        PriceRange(minimum_price=min_price, maximum_price=max_price)
        assert False, "Should have raised InvalidFilterException"
    except InvalidFilterException:
        pass


def test_query_builder() -> None:
    """Verify RentalQueryBuilder converts domain filter to query dictionary."""
    filter_obj = RentalFilter().with_city("Timóteo").with_bedrooms(2)
    builder = RentalQueryBuilder()
    query_params = builder.build_api_parameters(filter_obj)
    assert query_params.get("filter[by_room_greater_equals][bedroom]") == "2"
    assert query_params.get("filter[transaction]") == "2"
    assert query_params.get("filter[by_neighborhood_or_city_slug]") == "timoteo-mg"
    url = builder.build_canonical_website_url(filter_obj)
    assert "cabralportoimoveis.com.br/alugar/imoveis/timoteo-mg" in url
    assert "bedrooms=2" in url


def test_provider_live_search() -> None:
    """Test live search execution against Cabral Porto Imóveis portal."""
    provider = CabralPortoRentalProvider.create_default()
    criteria = RentalFilter().with_city("timoteo-mg").with_bedrooms(2)
    result = provider.search_rentals(criteria)
    assert result.total_count() >= 3
    assert result.returned_count() >= 3
    first_listing = list(result.listings())[0]
    assert len(first_listing.code()) > 0
    assert first_listing.core.valuation.rental_price.value() > 0


def test_provider_live_detail() -> None:
    """Test live detail retrieval for property 422."""
    provider = CabralPortoRentalProvider.create_default()
    code = PropertyCode("422")
    detail = provider.get_property_detail(code)
    assert detail.listing.code() == "422"
    assert "Apartamento" in detail.listing.title()
    assert len(detail.profile.description) > 0


def test_mcp_adapter() -> None:
    """Test MCP tool adapter output format."""
    adapter = CabralPortoMcpAdapter.create_default()
    search_dict = adapter.search_rentals(city="timoteo-mg", bedrooms=2)
    assert "total_count" in search_dict
    assert "listings" in search_dict
    assert len(search_dict["listings"]) > 0

    detail_dict = adapter.get_property_detail("422")
    assert detail_dict["code"] == "422"
    assert "title" in detail_dict


def main() -> None:
    """Execute all tests."""
    tests = [
        test_listing_price_validation,
        test_price_range_validation,
        test_query_builder,
        test_provider_live_search,
        test_provider_live_detail,
        test_mcp_adapter,
    ]
    passed = 0
    print("=== Running Cabral Porto Research Verification Test Suite ===\n")
    for test in tests:
        name = test.__name__
        try:
            test()
            print(f"[PASSED] {name}")
            passed += 1
        except Exception as error:
            print(f"[FAILED] {name}: {error}")
    print(f"\nResult: {passed}/{len(tests)} passed.")
    if passed != len(tests):
        sys.exit(1)


if __name__ == "__main__":
    main()
