"""Parser for single property detail JSON responses."""

from typing import Any
from cabralporto_research.domain.listing import ListingLocation, ListingSpecs
from cabralporto_research.domain.property import PhotoGallery, PhotoItem, PropertyDetail, PropertyPricing


class PhotoGalleryParser:
    """Parses photo items from images_extra list."""

    def parse_photos(self, raw_images: Any) -> PhotoGallery:
        """Extract photo items from raw list."""
        if not isinstance(raw_images, list):
            return PhotoGallery()
        photos: list[PhotoItem] = []
        for img in raw_images:
            if isinstance(img, dict):
                item = self._build_photo_item(img)
                if item:
                    photos.append(item)
        return PhotoGallery(photos=tuple(photos))

    def _build_photo_item(self, img: dict[str, Any]) -> PhotoItem | None:
        """Construct individual photo item from image dict."""
        pid = str(img.get("id", ""))
        caption = img.get("caption")
        furl = img.get("file_url", {})
        if not isinstance(furl, dict):
            return None
        large = furl.get("large", "")
        if not large:
            return None
        medium = furl.get("medium", large)
        return PhotoItem(photo_id=pid, large_url=large, medium_url=medium, caption=caption)


class PropertyDetailParser:
    """Parses JSON response from Tecimob /properties/{id} endpoint."""

    BASE_SITE_URL = "https://cabralportoimoveis.com.br"

    def __init__(self, photo_parser: PhotoGalleryParser | None = None) -> None:
        """Initialize with optional photo parser collaborator."""
        self._photo_parser = photo_parser or PhotoGalleryParser()

    def parse(self, json_data: dict[str, Any]) -> PropertyDetail:
        """Parse raw JSON response dictionary into PropertyDetail domain entity."""
        d = self._extract_data_payload(json_data)
        ref = str(d.get("reference", ""))
        canonical = f"{self.BASE_SITE_URL}/imovel/{d.get('url', ref)}"
        return PropertyDetail(
            property_id=str(d.get("id", "")), reference=ref,
            title=d.get("title_formatted") or f"Imóvel {ref}",
            pricing=self._extract_pricing(d), transaction=d.get("transaction") or "ALUGUEL",
            status=d.get("status") or "Disponível", location=self._extract_location(d),
            specs=self._extract_specs(d), areas=self._extract_areas(d),
            description=d.get("description") or "", canonical_url=canonical,
            photos=self._photo_parser.parse_photos(d.get("images_extra")),
        )

    def _extract_data_payload(self, json_data: dict[str, Any]) -> dict[str, Any]:
        """Validate response envelope and extract data payload."""
        data = json_data.get("data", {})
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid property detail response: missing data object.")
        return data

    def _extract_pricing(self, d: dict[str, Any]) -> PropertyPricing:
        """Extract prices and condominium fees."""
        price = d.get("price") or "Consulte"
        total = d.get("total_price") or price
        condo = d.get("condominium_price")
        taxes = d.get("total_taxes_price")
        return PropertyPricing(price, total, condo, taxes)

    def _extract_location(self, d: dict[str, Any]) -> ListingLocation:
        """Extract locality attributes from property dictionary."""
        addr = d.get("address", {})
        fmt = addr.get("formatted", "") if isinstance(addr, dict) else ""
        c_obj = d.get("city_description", {})
        city = c_obj.get("name", "") if isinstance(c_obj, dict) else ""
        n_obj = d.get("neighborhood_description", {})
        neigh = n_obj.get("name", "") if isinstance(n_obj, dict) else ""
        return ListingLocation(neighborhood=neigh, city=city, formatted=fmt)

    def _extract_specs(self, d: dict[str, Any]) -> ListingSpecs:
        """Extract bedroom, suite, bathroom, and garage counts."""
        rooms = d.get("rooms") if isinstance(d.get("rooms"), dict) else {}
        b = self._safe_int(rooms.get("bedroom", {}).get("value"))
        s = self._safe_int(rooms.get("suite", {}).get("value"))
        bath = self._safe_int(rooms.get("bathroom", {}).get("value"))
        g = self._safe_int(rooms.get("garage", {}).get("value"))
        built = d.get("areas", {}).get("built_area", {}) if isinstance(d.get("areas"), dict) else {}
        area = f"{built.get('value')} {built.get('measure', 'm²')}" if isinstance(built, dict) and built.get("value") else None
        return ListingSpecs(bedrooms=b, suites=s, bathrooms=bath, garages=g, area_m2=area)

    def _safe_int(self, value: Any) -> int | None:
        """Safely convert value to integer or None."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _extract_areas(self, d: dict[str, Any]) -> dict[str, str]:
        """Extract all area specifications as label-value dictionary."""
        areas: dict[str, str] = {}
        raw = d.get("areas")
        if not isinstance(raw, dict):
            return areas
        for k, v in raw.items():
            if isinstance(v, dict) and v.get("value"):
                title = v.get("title", k)
                measure = v.get("measure", "m²")
                areas[title] = f"{v.get('value')} {measure}"
        return areas
