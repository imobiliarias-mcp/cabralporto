"""Domain package exports for Cabral Porto research module."""

from cabralporto_research.domain.criteria import SearchCriteria, SearchFilterBundle, SearchPaginationBundle
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

__all__ = [
    "AreaRange",
    "City",
    "FacetCollection",
    "ListingLocation",
    "ListingSpecs",
    "Neighborhood",
    "PageNumber",
    "PaginationMeta",
    "PhotoGallery",
    "PhotoItem",
    "PriceRange",
    "PropertyCode",
    "PropertyDetail",
    "PropertyPricing",
    "PropertyType",
    "PropertyTypeItem",
    "RentalListingCollection",
    "RentalListingSummary",
    "RoomCount",
    "SearchCriteria",
    "SearchFilterBundle",
    "SearchPaginationBundle",
    "SortOrder",
    "TransactionType",
]
