"""Domain models and collections for rental listing search results."""

from dataclasses import dataclass
from urllib.parse import urlsplit


def _validated_public_url(property_url: str, property_context: str) -> str:
    """Require an absolute public HTTP(S) URL without embedded credentials."""
    try:
        parts = urlsplit(property_url)
        hostname = parts.hostname
    except ValueError as error:
        raise ValueError(f"Invalid public property URL for '{property_context}'.") from error
    if (
        property_url != property_url.strip()
        or parts.scheme.lower() not in {"http", "https"}
        or not hostname
        or parts.username
        or parts.password
    ):
        raise ValueError(f"Invalid public property URL for '{property_context}'.")
    return property_url


@dataclass(frozen=True)
class ListingLocation:
    """Location value object for property listing."""

    neighborhood: str
    city: str
    formatted: str

    def to_dictionary(self) -> dict:
        """Serialize location fields."""
        return {
            "neighborhood": self.neighborhood,
            "city": self.city,
            "formatted_address": self.formatted,
        }


@dataclass(frozen=True)
class ListingSpecs:
    """Architectural specifications for property listing."""

    bedrooms: int | None = None
    suites: int | None = None
    bathrooms: int | None = None
    garages: int | None = None
    area_m2: str | None = None

    def to_dictionary(self) -> dict:
        """Serialize spec fields."""
        return {
            "bedrooms": self.bedrooms,
            "suites": self.suites,
            "bathrooms": self.bathrooms,
            "garages": self.garages,
            "area_m2": self.area_m2,
        }


@dataclass(frozen=True)
class RentalListingSummary:
    """Summary entity representing a single property card in search results."""

    property_id: str
    reference: str
    title: str
    price: str
    transaction: str
    location: ListingLocation
    specs: ListingSpecs
    thumbnail_url: str | None
    detail_url: str

    def to_dictionary(self) -> dict:
        """Convert a listing summary with a valid absolute public URL."""
        property_context = self.reference or self.property_id or "unknown"
        public_url = _validated_public_url(self.detail_url, property_context)
        listing_dictionary = {
            "property_id": self.property_id,
            "reference": self.reference,
            "title": self.title,
            "price": self.price,
            "transaction": self.transaction,
            "thumbnail_url": self.thumbnail_url,
            "detail_url": public_url,
            "url": public_url,
        }
        listing_dictionary.update(self.location.to_dictionary())
        listing_dictionary.update(self.specs.to_dictionary())
        return listing_dictionary


@dataclass(frozen=True)
class PaginationMeta:
    """Pagination metadata returned from Tecimob API."""

    total: int
    per_page: int
    current_page: int
    total_pages: int


@dataclass(frozen=True)
class RentalListingCollection:
    """First-class collection representing rental search results with pagination."""

    items: tuple[RentalListingSummary, ...] = ()
    pagination: PaginationMeta | None = None

    def __len__(self) -> int:
        """Return number of listings in this page."""
        return len(self.items)

    def is_empty(self) -> bool:
        """Check whether collection is empty."""
        return len(self.items) == 0

    def __getitem__(self, index: int) -> RentalListingSummary:
        """Access listing by index."""
        return self.items[index]

    def __iter__(self):
        """Iterate over listing summaries."""
        return iter(self.items)

    @property
    def total_count(self) -> int:
        """Return total available listings from pagination metadata."""
        if self.pagination:
            return self.pagination.total
        return len(self.items)

    @property
    def current_page(self) -> int:
        """Return current page number from pagination metadata."""
        if self.pagination:
            return self.pagination.current_page
        return 1

    @property
    def total_pages(self) -> int:
        """Return total pages count from pagination metadata."""
        if self.pagination:
            return self.pagination.total_pages
        return 1



    def to_list(self) -> list[dict]:
        """Convert all listings to list of serializable dictionaries."""
        return [item.to_dictionary() for item in self.items]

    def to_list_of_dictionaries(self) -> list[dict]:
        """Convert all listings to list of serializable dictionaries."""
        return self.to_list()


