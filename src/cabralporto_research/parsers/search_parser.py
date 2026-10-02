"""Parser for property search JSON payloads."""

from typing import Any

from cabralporto_research.domain.listing import (
    ListingLocation,
    ListingSpecs,
    PaginationMeta,
    RentalListingCollection,
    RentalListingSummary,
)
from cabralporto_research.parsers.public_url import PublicPropertyUrlResolver


class ListingItemParser:
    """Parses individual listing item payloads."""

    BASE_SITE_URL = "https://cabralportoimoveis.com.br"

    def __init__(self, public_base_url: str = BASE_SITE_URL) -> None:
        """Initialize URL resolution with the configured public site base."""
        self._url_resolver = PublicPropertyUrlResolver(public_base_url)

    def parse_item(self, item: dict[str, Any]) -> RentalListingSummary:
        """Extract a single listing summary from property data dictionary."""
        pid = str(item.get("id", ""))
        ref = str(item.get("reference", ""))
        title = item.get("title_formatted") or f"Imóvel {ref}"
        price = item.get("price") or "Consulte"
        tx = item.get("transaction") or "ALUGUEL"
        loc = self._extract_location(item)
        specs = self._extract_specs(item)
        thumb = self._extract_thumbnail(item)
        url = self._extract_detail_url(item)
        return RentalListingSummary(pid, ref, title, price, tx, loc, specs, thumb, url)

    def _extract_location(self, item: dict[str, Any]) -> ListingLocation:
        """Extract locality attributes from property dictionary."""
        addr = item.get("address")
        fmt = addr.get("formatted", "") if isinstance(addr, dict) else ""
        neigh, city = "", ""
        if fmt and "-" in fmt:
            parts = fmt.split("-", 1)
            neigh = parts[0].strip()
            city_part = parts[1].strip()
            city = city_part.split("/")[0].strip() if "/" in city_part else city_part
        return ListingLocation(neighborhood=neigh, city=city, formatted=fmt)

    def _extract_specs(self, item: dict[str, Any]) -> ListingSpecs:
        """Extract bedroom, suite, bathroom, and garage counts."""
        rooms = item.get("rooms") if isinstance(item.get("rooms"), dict) else {}
        b = self._safe_int(rooms.get("bedroom", {}).get("value"))
        s = self._safe_int(rooms.get("suite", {}).get("value"))
        bath = self._safe_int(rooms.get("bathroom", {}).get("value"))
        g = self._safe_int(rooms.get("garage", {}).get("value"))
        area = self._extract_primary_area(item)
        return ListingSpecs(bedrooms=b, suites=s, bathrooms=bath, garages=g, area_m2=area)

    def _safe_int(self, value: Any) -> int | None:
        """Safely convert value to integer or None."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _extract_primary_area(self, item: dict[str, Any]) -> str | None:
        """Extract primary area measure from property areas dictionary."""
        areas = item.get("areas")
        if not isinstance(areas, dict):
            return None
        built = areas.get("built_area", {})
        if isinstance(built, dict) and built.get("value"):
            return f"{built.get('value')} {built.get('measure', 'm²')}"
        total = areas.get("total_area", {})
        if isinstance(total, dict) and total.get("value"):
            return f"{total.get('value')} {total.get('measure', 'm²')}"
        return None

    def _extract_thumbnail(self, item: dict[str, Any]) -> str | None:
        """Extract thumbnail photo URL from extra images or card image."""
        images = item.get("images_extra")
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                furl = first.get("file_url", {})
                if isinstance(furl, dict):
                    return furl.get("medium") or furl.get("large")
        return None

    def _extract_detail_url(self, item: dict[str, Any]) -> str:
        """Resolve a public detail URL carried by the API card."""
        context = str(item.get("reference") or item.get("id") or "unknown")
        return self._url_resolver.resolve(item.get("url"), context)


class SearchResponseParser:
    """Parses JSON responses from Tecimob /properties endpoint."""

    def __init__(
        self,
        item_parser: ListingItemParser | None = None,
        public_base_url: str = ListingItemParser.BASE_SITE_URL,
    ) -> None:
        """Initialize with item parser and public-site URL configuration."""
        self._item_parser = item_parser or ListingItemParser(public_base_url=public_base_url)

    def parse(self, json_data: dict[str, Any] | None) -> RentalListingCollection:
        """Parse JSON response dictionary into RentalListingCollection."""
        if not json_data or not isinstance(json_data, dict):
            return RentalListingCollection()
        raw_items = json_data.get("data", [])
        if not isinstance(raw_items, list):
            return RentalListingCollection()
        parsed = [self._item_parser.parse_item(it) for it in raw_items if isinstance(it, dict)]
        meta = self._parse_pagination(json_data.get("meta"))
        return RentalListingCollection(items=tuple(parsed), pagination=meta)

    def _parse_pagination(self, meta: Any) -> PaginationMeta | None:
        """Parse pagination block from meta object."""
        if not isinstance(meta, dict):
            return None
        p_dict = meta.get("pagination")
        if not isinstance(p_dict, dict):
            return None
        return PaginationMeta(
            total=p_dict.get("total", 0) or 0,
            per_page=p_dict.get("per_page", 21) or 21,
            current_page=p_dict.get("current_page", 1) or 1,
            total_pages=p_dict.get("total_pages", 1) or 1,
        )
