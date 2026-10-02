#!/usr/bin/env python3
"""Verification script executing live search and retrieval on Cabral Porto Imóveis."""

import sys
from pathlib import Path

# Add project root and src to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from cabralporto_research.client import CabralPortoRentalClient
from cabralporto_research.domain.criteria import SearchCriteria
from cabralporto_research.domain.enums import PropertyType, SortOrder


def main() -> None:
    """Execute live verification workflow."""
    print("=== Starting Cabral Porto Imóveis Research Verification ===")
    client = CabralPortoRentalClient()

    # 1. Target URL Search (Aluguel / Timóteo / >= 2 quartos / sort: -created_at,id)
    print("\n--- 1. Target Prompt URL Search (Alugar / Timóteo / >= 2 dorms / sort: -created_at,id) ---")
    target_criteria = SearchCriteria.create_rental(
        city_slug="timoteo-mg",
        property_type=PropertyType.IMOVEIS,
        bedrooms=2,
        min_bedrooms=True,
        page=1,
        limit=21,
        sort=SortOrder.RECENT,
    )
    results = client.search(target_criteria)
    print(f"Total matching listings: {results.total_count}")
    print(f"Listings returned on page {results.current_page}: {len(results)}")
    for item in results:
        specs_desc = f"{item.specs.bedrooms} dorms" if item.specs.bedrooms else "Sem dormitórios"
        print(f"  [{item.reference}] {item.title[:45]:<45} | {item.price:>12} | {item.location.neighborhood} ({specs_desc})")
        print(f"  Link: {item.detail_url}")

    # 2. All Timóteo Rental Listings
    print("\n--- 2. All Timóteo Rental Listings Search ---")
    all_rentals = client.search_rentals(city_slug="timoteo-mg", page=1, limit=21)
    print(f"Total rental listings in Timóteo: {all_rentals.total_count}")
    for item in all_rentals:
        print(f"  [{item.reference}] {item.title[:45]:<45} | {item.price:>12} | {item.location.neighborhood}")
        print(f"  Link: {item.detail_url}")

    # 3. Property Detail Retrieval (Apartment Ref 422)
    print("\n--- 3. Property Detail Retrieval (Apartment Ref 422) ---")
    detail = client.get_details("422")
    print(f"Title: {detail.title}")
    print(f"Reference: {detail.reference}")
    print(f"Price: {detail.pricing.price} (Total: {detail.pricing.total_price}, Condomínio: {detail.pricing.condominium_price})")
    print(f"Location: {detail.location.formatted}")
    print(f"Rooms: {detail.specs.bedrooms} dorms, {detail.specs.bathrooms} banheiros, {detail.specs.garages} vagas")
    print(f"Total photos in gallery: {len(detail.photos)}")
    if len(detail.photos) > 0:
        print(f"  Photo 1: {detail.photos[0].large_url}")
        print(f"  Photo 2: {detail.photos[1].large_url}")

    # 4. Filter Facets Retrieval
    print("\n--- 4. Filter Facets Retrieval ---")
    facets = client.get_facets()
    print(f"Total cities: {len(facets.cities)}")
    print(f"Total neighborhoods: {len(facets.neighborhoods)}")
    print(f"Total property types: {len(facets.types)}")
    sample_cities = [c.name for c in facets.cities[:5]]
    sample_types = [t.title for t in facets.types[:5]]
    print(f"Sample cities: {', '.join(sample_cities)}")
    print(f"Sample types: {', '.join(sample_types)}")

    print("\n=== Cabral Porto Imóveis Research Verification Completed Successfully ===")


if __name__ == "__main__":
    main()
