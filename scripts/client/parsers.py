"""JSON parsers converting Tecimob API payloads into domain entities."""

import re
from typing import Any

from scripts.client.public_urls import PublicPropertyUrlResolver
from scripts.domain.collections import (
    FacetCollection,
    RentalListingCollection,
    RentalSearchResult,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingResources,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.value_objects import ListingPrice, PropertyCode


class ListingCardParser:
    """Parses individual listing item into domain entity."""

    DEFAULT_PUBLIC_BASE_URL = "https://cabralportoimoveis.com.br"

    def __init__(self, public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> None:
        """Initialize public link resolution for listing cards."""
        self._url_resolver = PublicPropertyUrlResolver(public_base_url)

    def _build_valuation(self, item: dict[str, Any]) -> ListingValuation:
        """Construct valuation value object from property item."""
        prop_type = item.get("profile") or "Imóvel"
        price_val = self._parse_price_float(item.get("price"))
        condo_val = self._parse_price_float(item.get("condominium_price"))
        condo_fee = condo_val if condo_val > 0.0 else None
        tax_val = self._parse_price_float(item.get("total_taxes_price"))
        iptu_fee = tax_val if tax_val > 0.0 else None
        return ListingValuation(
            rental_price=ListingPrice(price_val),
            property_type=prop_type,
            condo_fee=condo_fee,
            iptu=iptu_fee,
        )

    def parse_single_listing(self, item: dict[str, Any]) -> RentalListing:
        """Convert a single API property item into RentalListing entity."""
        code_str = str(item.get("reference") or item.get("id", ""))
        title = item.get("title_formatted") or f"Imóvel {code_str}"
        location = item.get("address", {}).get("formatted") or "Timóteo/MG"
        media_url = self._extract_thumbnail(item)
        property_url = self._url_resolver.resolve(item.get("url"), code_str)
        identity = ListingIdentity(code=PropertyCode(code_str), title=title)
        val = self._build_valuation(item)
        core = ListingCore(identity=identity, valuation=val)
        resources = ListingResources(media_url=media_url, property_url=property_url)
        details = ListingDetails(location_summary=location, resources=resources)
        return RentalListing(core=core, details=details)

    def _parse_price_float(self, raw_price: Any) -> float:
        """Parse currency string like 'R$1.400,00' to float."""
        if not raw_price:
            return 0.0
        cleaned = re.sub(r"[^\d,\.]", "", str(raw_price))
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _extract_thumbnail(self, item: dict[str, Any]) -> str:
        """Extract primary photo URL from images_extra."""
        images = item.get("images_extra")
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                furl = first.get("file_url", {})
                if isinstance(furl, dict):
                    return furl.get("medium") or furl.get("large") or ""
        return ""


class ResponseParser:
    """Parses Tecimob API JSON payloads into domain collections and details."""

    def __init__(
        self,
        listing_parser: ListingCardParser | None = None,
        public_base_url: str = ListingCardParser.DEFAULT_PUBLIC_BASE_URL,
    ) -> None:
        """Initialize with listing parser and configured public origin."""
        self._listing_parser = listing_parser or ListingCardParser(public_base_url=public_base_url)

    def parse_search_json(self, json_data: dict[str, Any]) -> RentalSearchResult:
        """Extract rental listings and total count from search API response."""
        raw_items = json_data.get("data", [])
        if not isinstance(raw_items, list):
            empty_col = RentalListingCollection(listings=())
            return RentalSearchResult(collection=empty_col, total_listings_count=0)
        items = [self._listing_parser.parse_single_listing(it) for it in raw_items if isinstance(it, dict)]
        col = RentalListingCollection(listings=tuple(items))
        total = self._extract_total_count(json_data, len(items))
        return RentalSearchResult(collection=col, total_listings_count=total)

    def _extract_total_count(self, json_data: dict[str, Any], items_len: int) -> int:
        """Extract total pagination count from meta dictionary."""
        meta = json_data.get("meta")
        if isinstance(meta, dict):
            p = meta.get("pagination")
            if isinstance(p, dict) and p.get("total") is not None:
                return int(p["total"])
        return items_len

    def parse_detail_json(self, json_data: dict[str, Any]) -> RentalPropertyDetail:
        """Parse single property detail API response into RentalPropertyDetail."""
        d = json_data.get("data", {})
        if not d or not isinstance(d, dict):
            raise ValueError("Invalid property detail response: missing data object.")
        base = self._listing_parser.parse_single_listing(d)
        desc = d.get("description", "")
        amenities = self._extract_amenities_summary(d)
        profile = DetailedProfile(description=desc, amenities_summary=amenities)
        return RentalPropertyDetail(listing=base, profile=profile)

    def _extract_amenities_summary(self, data: dict[str, Any]) -> str:
        """Build summary string of rooms and amenities."""
        rooms = data.get("rooms")
        if not isinstance(rooms, dict):
            return "Nenhuma comodidade informada"
        parts = [str(r["title_formated"]) for r in rooms.values() if isinstance(r, dict) and r.get("title_formated")]
        return ", ".join(parts) if parts else "Nenhuma comodidade informada"

    def parse_facets_json(
        self, states_json: dict[str, Any] | None = None, neighborhoods_json: dict[str, Any] | None = None
    ) -> FacetCollection:
        """Extract cities and neighborhoods into FacetCollection."""
        cities = self._extract_cities(states_json)
        neighborhoods = self._extract_neighborhoods(neighborhoods_json)
        return FacetCollection(facet_map={"cities": tuple(cities), "neighborhoods": tuple(neighborhoods)})

    def _extract_cities(self, states_json: dict[str, Any] | None) -> list[str]:
        """Extract sorted unique city names from states JSON."""
        if not states_json or not isinstance(states_json, dict):
            return []
        cities: list[str] = []
        for state in states_json.get("data", []):
            if isinstance(state, dict):
                cities.extend(str(c["name"]) for c in state.get("cities", []) if isinstance(c, dict) and c.get("name"))
        return sorted(set(cities))

    def _extract_neighborhoods(self, neigh_json: dict[str, Any] | None) -> list[str]:
        """Extract sorted unique neighborhood names from neighborhoods JSON."""
        if not neigh_json or not isinstance(neigh_json, dict):
            return []
        names = [str(n["name"]) for n in neigh_json.get("data", []) if isinstance(n, dict) and n.get("name")]
        return sorted(set(names))
