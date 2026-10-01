"""Domain models for full property detail views."""

from dataclasses import dataclass
from cabralporto_research.domain.listing import ListingLocation, ListingSpecs


@dataclass(frozen=True)
class PhotoItem:
    """Individual photo asset in gallery."""

    photo_id: str
    large_url: str
    medium_url: str
    caption: str | None = None


@dataclass(frozen=True)
class PhotoGallery:
    """First-class collection representing a property photo gallery."""

    photos: tuple[PhotoItem, ...] = ()

    def __len__(self) -> int:
        """Return total photos count."""
        return len(self.photos)

    def is_empty(self) -> bool:
        """Check if gallery has no photos."""
        return len(self.photos) == 0

    def __getitem__(self, index: int) -> PhotoItem:
        """Access photo by index."""
        return self.photos[index]

    def __iter__(self):
        """Iterate over photos in gallery."""
        return iter(self.photos)

    @property
    def primary_photo_url(self) -> str | None:
        """Return URL of primary/first photo if available."""
        if self.photos:
            return self.photos[0].large_url
        return None


    def to_list(self) -> list[dict]:
        """Convert photos to serializable list."""
        return [
            {
                "id": p.photo_id,
                "large": p.large_url,
                "medium": p.medium_url,
                "caption": p.caption,
            }
            for p in self.photos
        ]


@dataclass(frozen=True)
class PropertyPricing:
    """Encapsulates pricing attributes."""

    price: str
    total_price: str
    condominium_price: str | None = None
    total_taxes: str | None = None

    def to_dictionary(self) -> dict:
        """Serialize pricing attributes."""
        return {
            "price": self.price,
            "total_price": self.total_price,
            "condominium_price": self.condominium_price,
            "total_taxes": self.total_taxes,
        }


@dataclass(frozen=True)
class PropertyDetail:
    """Complete entity for a single property detail view."""

    property_id: str
    reference: str
    title: str
    pricing: PropertyPricing
    transaction: str
    status: str
    location: ListingLocation
    specs: ListingSpecs
    areas: dict[str, str]
    description: str
    canonical_url: str
    photos: PhotoGallery

    def to_dictionary(self) -> dict:
        """Convert property detail to standard serializable dictionary."""
        d = self._base_dictionary()
        d.update(self.pricing.to_dictionary())
        d.update(self.location.to_dictionary())
        d.update(self.specs.to_dictionary())
        return d

    def _base_dictionary(self) -> dict:
        """Serialize core property attributes."""
        return {
            "property_id": self.property_id,
            "reference": self.reference,
            "title": self.title,
            "transaction": self.transaction,
            "status": self.status,
            "areas": self.areas,
            "description": self.description,
            "canonical_url": self.canonical_url,
            "photos": self.photos.to_list(),
        }
