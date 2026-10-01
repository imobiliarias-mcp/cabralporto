"""Unit tests for domain value objects, criteria, and entities."""

import pytest
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType, SortOrder, TransactionType
from cabralporto_research.domain.listing import (
    ListingLocation,
    ListingSpecs,
    PaginationMeta,
    RentalListingCollection,
    RentalListingSummary,
)
from cabralporto_research.domain.metadata import City, FacetCollection, Neighborhood, PropertyTypeItem
from cabralporto_research.domain.property import PhotoGallery, PhotoItem, PropertyDetail, PropertyPricing
from cabralporto_research.domain.values import AreaRange, PageNumber, PriceRange, PropertyCode, RoomCount


def test_price_range_validation_and_parameters() -> None:
    """Verify PriceRange validation and query parameter output."""
    price_range = PriceRange(minimum=1000, maximum=2500)
    params = price_range.query_parameters()
    assert params["filter[by_higher_than_price]"] == "1000"
    assert params["filter[by_lower_than_price]"] == "2500"

    with pytest.raises(ValueError):
        PriceRange(minimum=-10)

    with pytest.raises(ValueError):
        PriceRange(minimum=3000, maximum=1000)


def test_area_range_validation_and_parameters() -> None:
    """Verify AreaRange validation and query parameters."""
    area = AreaRange(minimum=60, maximum=150, area_type="built_area")
    params = area.query_parameters()
    assert params["filter[by_area][greater_equals]"] == "60"
    assert params["filter[by_area][lower_equals]"] == "150"
    assert params["filter[by_area][name]"] == "built_area"

    with pytest.raises(ValueError):
        AreaRange(minimum=-5)


def test_room_count_exact_and_minimum() -> None:
    """Verify RoomCount parameter generation for exact and minimum modes."""
    min_bedrooms = RoomCount(count=2, is_minimum=True)
    min_params = min_bedrooms.query_parameters("bedroom")
    assert min_params == {"filter[by_room_greater_equals][bedroom]": "2"}

    exact_bedrooms = RoomCount(count=3, is_minimum=False)
    exact_params = exact_bedrooms.query_parameters("bedroom")
    assert exact_params == {"filter[by_room_equals][bedroom]": "3"}

    with pytest.raises(ValueError):
        RoomCount(count=-1)


def test_page_number_validation() -> None:
    """Verify PageNumber boundary enforcement."""
    page = PageNumber(value=2, limit=21)
    params = page.query_parameters()
    assert params == {"offset": "2", "limit": "21"}

    with pytest.raises(ValueError):
        PageNumber(value=0)

    with pytest.raises(ValueError):
        PageNumber(value=1, limit=150)


def test_property_code_sanitization() -> None:
    """Verify PropertyCode validation and sanitization."""
    code = PropertyCode("  422  ")
    assert code.sanitized() == "422"

    with pytest.raises(ValueError):
        PropertyCode("   ")


def test_search_criteria_rental_factory() -> None:
    """Verify SearchCriteria factory creates expected filter bundle."""
    criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        min_bedrooms=True,
        min_price=1000,
        max_price=3000,
        page=1,
        limit=21,
        sort=SortOrder.RECENT,
    )
    assert criteria.filters.transaction == TransactionType.ALUGAR
    assert criteria.filters.property_type == PropertyType.APARTAMENTO
    assert criteria.filters.city_slug == "timoteo-mg"
    assert criteria.filters.bedrooms.count == 2
    assert criteria.filters.bedrooms.is_minimum is True
    assert criteria.pagination.sort == SortOrder.RECENT
    assert criteria.pagination.page.value == 1


def test_listing_collection_operations() -> None:
    """Verify RentalListingCollection wrapping and iteration."""
    location = ListingLocation(neighborhood="Eldorado", city="Timóteo", formatted="Eldorado - Timóteo/MG")
    specs = ListingSpecs(bedrooms=2, suites=1, bathrooms=1, garages=1, area_m2="65 m²")
    item = RentalListingSummary(
        property_id="uuid-1",
        reference="422",
        title="Apartamento em Eldorado",
        price="R$ 1.400,00",
        transaction="ALUGUEL",
        location=location,
        specs=specs,
        thumbnail_url="https://image.url",
        detail_url="https://detail.url",
    )
    pagination = PaginationMeta(total=10, per_page=21, current_page=1, total_pages=1)
    collection = RentalListingCollection(items=(item,), pagination=pagination)

    assert len(collection) == 1
    assert collection[0].reference == "422"
    assert collection.total_count == 10
    assert collection.current_page == 1
    assert collection.total_pages == 1
    dictionary_list = collection.to_list()
    assert len(dictionary_list) == 1
    assert dictionary_list[0]["reference"] == "422"


def test_facet_collection_lookup() -> None:
    """Verify FacetCollection search and lookup functions."""
    city = City(id="timoteo-mg", name="Timóteo", state_acronym="MG")
    neighborhood = Neighborhood(id="timoteo-mg-eldorado", name="Eldorado")
    prop_type = PropertyTypeItem(id="apartamento", title="Apartamento")
    facets = FacetCollection(cities=(city,), neighborhoods=(neighborhood,), types=(prop_type,))

    found_city = facets.find_city_by_slug("timoteo-mg")
    assert found_city is not None
    assert found_city.name == "Timóteo"

    found_neigh = facets.find_neighborhood_by_name("eldorado")
    assert found_neigh is not None
    assert found_neigh.id == "timoteo-mg-eldorado"

    missing = facets.find_city_by_slug("rio-de-janeiro-rj")
    assert missing is None
