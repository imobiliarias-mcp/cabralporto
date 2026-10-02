#!/usr/bin/env python3
"""CLI runner for retrieving property details from Cabral Porto Imóveis."""

import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.value_objects import PropertyCode
from scripts.providers.cabralporto import CabralPortoRentalProvider


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="Retrieve rental property details from Cabral Porto Imóveis.")
    parser.add_argument("code", type=str, help="Property reference code or UUID (e.g. 422)")
    return parser


def display_detail(detail) -> None:
    """Print property details to console."""
    print("\n" + "=" * 75)
    print(f"Detalhes do Imóvel: {detail.listing.title()}")
    print("=" * 75)
    formatted = detail.format_detailed_view()
    print(formatted)
    print("-" * 75)
    listing_data = detail.listing.to_dictionary()
    print(f"Link: {listing_data['url']}")
    print(f"Foto Principal: {listing_data['media_url']}")
    print("=" * 75 + "\n")


def main() -> None:
    """Main execution function."""
    argument_parser = build_argument_parser()
    parsed_arguments = argument_parser.parse_args()
    code_vo = PropertyCode(parsed_arguments.code)
    provider = CabralPortoRentalProvider.create_default()
    detail = provider.get_property_detail(code_vo)
    display_detail(detail)


if __name__ == "__main__":
    main()
