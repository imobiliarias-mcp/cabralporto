#!/usr/bin/env python3
"""CLI runner for retrieving available search facets and localities."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.providers.cabralporto import CabralPortoRentalProvider


def main() -> None:
    """Retrieve and display search facets."""
    provider = CabralPortoRentalProvider.create_default()
    facets = provider.get_facets()
    cities = facets.city_names()
    neighborhoods = facets.neighborhood_names()

    print(f"\nCidades Disponíveis ({len(cities)}):")
    print(", ".join(cities))

    print(f"\nBairros Disponíveis ({len(neighborhoods)}):")
    print(", ".join(neighborhoods[:30]))
    if len(neighborhoods) > 30:
        print(f"... e mais {len(neighborhoods) - 30} bairros")


if __name__ == "__main__":
    main()
