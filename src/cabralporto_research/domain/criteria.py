"""Search criteria and parameter bundles for query dispatch."""

from dataclasses import dataclass, field
from cabralporto_research.domain.enums import PropertyType, SortOrder, TransactionType
from cabralporto_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount


@dataclass(frozen=True)
class SearchFilterBundle:
    """Encapsulates filter attributes for property search queries."""

    transaction: TransactionType = TransactionType.ALUGAR
    property_type: PropertyType = PropertyType.IMOVEIS
    city_slug: str = "timoteo-mg"
    neighborhood_slug: str | None = None
    price: PriceRange = field(default_factory=PriceRange)
    area: AreaRange = field(default_factory=AreaRange)
    bedrooms: RoomCount | None = None
    suites: RoomCount | None = None
    garages: RoomCount | None = None


@dataclass(frozen=True)
class SearchPaginationBundle:
    """Encapsulates pagination and sorting options for search queries."""

    page: PageNumber = field(default_factory=PageNumber)
    sort: SortOrder = SortOrder.RECENT
    custom_query: str = "card"


@dataclass(frozen=True)
class SearchCriteria:
    """Combines filter and pagination bundles for search execution."""

    filters: SearchFilterBundle = field(default_factory=SearchFilterBundle)
    pagination: SearchPaginationBundle = field(default_factory=SearchPaginationBundle)

    @classmethod
    def create_rental(
        cls, city_slug: str = "timoteo-mg", property_type: PropertyType = PropertyType.IMOVEIS,
        bedrooms: int | None = None, min_bedrooms: bool = True, suites: int | None = None,
        garages: int | None = None, min_price: int | None = None, max_price: int | None = None,
        page: int = 1, limit: int = 21, sort: SortOrder = SortOrder.RECENT,
    ) -> "SearchCriteria":
        """Factory constructor for standard rental searches."""
        args = (city_slug, property_type, bedrooms, min_bedrooms, suites, garages, min_price, max_price)
        filters = cls._build_rental_filters(*args)
        pagination = SearchPaginationBundle(page=PageNumber(page, limit), sort=sort)
        return cls(filters=filters, pagination=pagination)

    @classmethod
    def _build_rental_filters(
        cls, city_slug: str, property_type: PropertyType, bedrooms: int | None, min_bedrooms: bool,
        suites: int | None, garages: int | None, min_price: int | None, max_price: int | None,
    ) -> SearchFilterBundle:
        """Construct filter bundle for rental search."""
        b, s, g = cls._build_room_counts(bedrooms, min_bedrooms, suites, garages)
        price_vo = PriceRange(min_price, max_price)
        return SearchFilterBundle(
            transaction=TransactionType.ALUGAR, property_type=property_type,
            city_slug=city_slug, price=price_vo, bedrooms=b, suites=s, garages=g,
        )

    @staticmethod
    def _build_room_counts(bedrooms: int | None, min_bedrooms: bool, suites: int | None, garages: int | None):
        """Construct room count value objects."""
        b_vo = RoomCount(bedrooms, min_bedrooms) if bedrooms is not None else None
        s_vo = RoomCount(suites, True) if suites is not None else None
        g_vo = RoomCount(garages, True) if garages is not None else None
        return b_vo, s_vo, g_vo
