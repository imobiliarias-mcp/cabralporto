"""Unit tests for response parsers."""

from cabralporto_research.parsers.detail_parser import PropertyDetailParser
from cabralporto_research.parsers.metadata_parser import MetadataParser
from cabralporto_research.parsers.search_parser import (
    ListingItemParser,
    SearchResponseParser,
)


def test_search_response_parser() -> None:
    """Verify search parser parses items and pagination metadata."""
    sample_json = {
        "data": [
            {
                "id": "778af35a-9cf1-4c29-944b-db1cf5947416",
                "reference": "422",
                "title_formatted": "Apartamento em Eldorado, Timóteo/MG",
                "price": "R$1.400,00",
                "transaction": "ALUGUEL",
                "address": {"formatted": "Eldorado - Timóteo/MG"},
                "rooms": {
                    "bedroom": {"value": 2},
                    "suite": {"value": 0},
                    "bathroom": {"value": 1},
                    "garage": {"value": 1},
                },
                "areas": {
                    "built_area": {"value": "65", "measure": "m²"}
                },
                "images_extra": [
                    {
                        "id": "img-1",
                        "file_url": {
                            "large": "https://imagens.tecimob.com.br/large.jpg",
                            "medium": "https://imagens.tecimob.com.br/medium.webp",
                        },
                    }
                ],
                "url": "apartamento-para-alugar-no-bairro-eldorado-em-timoteo-mg/422",
            }
        ],
        "meta": {
            "pagination": {
                "total": 3,
                "per_page": 21,
                "current_page": 1,
                "total_pages": 1,
            }
        },
    }

    parser = SearchResponseParser()
    collection = parser.parse(sample_json)
    assert len(collection) == 1
    assert collection.total_count == 3
    assert collection.current_page == 1

    item = collection[0]
    assert item.reference == "422"
    assert item.title == "Apartamento em Eldorado, Timóteo/MG"
    assert item.price == "R$1.400,00"
    assert item.specs.bedrooms == 2
    assert item.specs.bathrooms == 1
    assert item.specs.garages == 1
    assert item.specs.area_m2 == "65 m²"
    assert item.location.neighborhood == "Eldorado"
    assert item.location.city == "Timóteo"
    assert item.thumbnail_url == "https://imagens.tecimob.com.br/medium.webp"
    assert "cabralportoimoveis.com.br/imovel" in item.detail_url


def test_listing_item_parser_handles_empty_rooms_without_property_url() -> None:
    """Verify empty room data remains safe without inventing a missing link."""
    parser = ListingItemParser()
    item = {"rooms": [], "images_extra": []}

    specs = parser._extract_specs(item)
    thumbnail_url = parser._extract_thumbnail(item)

    assert specs.bedrooms is None
    assert thumbnail_url is None


def test_property_detail_parser() -> None:
    """Verify property detail parser extracts all fields and photo gallery."""
    sample_detail_json = {
        "data": {
            "id": "778af35a-9cf1-4c29-944b-db1cf5947416",
            "reference": "422",
            "title_formatted": "Apartamento em Eldorado, Timóteo/MG",
            "price": "R$1.400,00",
            "total_price": "R$1.400,00",
            "condominium_price": "R$220,00",
            "total_taxes_price": "R$0,00",
            "transaction": "ALUGUEL",
            "status": "Disponível",
            "address": {"formatted": "Eldorado - Timóteo/MG"},
            "city_description": {"name": "Timóteo"},
            "neighborhood_description": {"name": "Eldorado"},
            "rooms": {
                "bedroom": {"value": 2},
                "bathroom": {"value": 1},
                "garage": {"value": 1},
            },
            "areas": {
                "built_area": {"title": "Área Construída", "value": "65", "measure": "m²"}
            },
            "description": "<p>Apartamento aconchegante</p>",
            "url": "apartamento-para-alugar-no-bairro-eldorado-em-timoteo-mg/422",
            "images_extra": [
                {
                    "id": "img-1",
                    "caption": "Sala",
                    "file_url": {
                        "large": "https://imagens.tecimob.com.br/large1.jpg",
                        "medium": "https://imagens.tecimob.com.br/medium1.webp",
                    },
                },
                {
                    "id": "img-2",
                    "caption": "Quarto",
                    "file_url": {
                        "large": "https://imagens.tecimob.com.br/large2.jpg",
                        "medium": "https://imagens.tecimob.com.br/medium2.webp",
                    },
                },
            ],
        }
    }

    parser = PropertyDetailParser()
    detail = parser.parse(sample_detail_json)
    assert detail.reference == "422"
    assert detail.pricing.price == "R$1.400,00"
    assert detail.pricing.condominium_price == "R$220,00"
    assert detail.location.neighborhood == "Eldorado"
    assert detail.location.city == "Timóteo"
    assert detail.specs.bedrooms == 2
    assert "Área Construída" in detail.areas
    assert len(detail.photos) == 2
    assert detail.photos[0].large_url == "https://imagens.tecimob.com.br/large1.jpg"
    assert detail.photos[0].caption == "Sala"


def test_scripts_property_detail_parser_extracts_condo_fee() -> None:
    from scripts.client.parsers import ResponseParser
    payload = {
        "data": {
            "reference": "422",
            "title_formatted": "Apartamento Eldorado",
            "price": "R$ 1.400,00",
            "condominium_price": "R$ 220,00",
            "url": "https://cabralportoimoveis.com.br/imovel/apartamento/422",
        }
    }
    parser = ResponseParser()
    detail = parser.parse_detail_json(payload)
    data = detail.to_dictionary()
    assert data["condo_fee"] == 220.0


def test_metadata_parser() -> None:
    """Verify metadata parser extracts cities, neighborhoods, and types."""
    states_data = {
        "data": [
            {
                "id": "MG",
                "name": "Minas Gerais",
                "acronym": "MG",
                "cities": [
                    {"id": "timoteo-mg", "name": "Timóteo"},
                    {"id": "ipatinga-mg", "name": "Ipatinga"},
                ],
            }
        ]
    }
    neigh_data = {
        "data": [
            {"id": "timoteo-mg-eldorado", "name": "Eldorado"},
            {"id": "timoteo-mg-centro", "name": "Centro"},
        ]
    }
    types_data = {
        "data": [
            {"id": "apartamento", "title": "Apartamento", "symbol": "building"}
        ]
    }

    parser = MetadataParser()
    facets = parser.parse_facets(states_data, neigh_data, types_data)
    assert len(facets.cities) == 2
    assert facets.cities[0].name == "Timóteo"
    assert len(facets.neighborhoods) == 2
    assert facets.neighborhoods[0].name == "Eldorado"
    assert len(facets.types) == 1
    assert facets.types[0].id == "apartamento"
