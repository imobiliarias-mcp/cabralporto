# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Reverse-engineered rental search engine and API client for **Cabral Porto Corretor de Imóveis** (`cabralportoimoveis.com.br`), running on the **Tecimob SaaS** headless real estate engine. The project provides both a standalone Python package (`src/cabralporto_research`) and an MCP (Model Context Protocol) provider adapter (`scripts/providers/cabralporto.py`) adhering to strict Object Calisthenics and SOLID principles.

## Development & Testing Commands

The project uses Python 3.13 in a local virtual environment (`.venv`) managed with `hatchling` and `pytest`.

### Environment
- Virtualenv python: `.venv/bin/python`
- Virtualenv pytest: `.venv/bin/pytest`
- Activate virtualenv: `source .venv/bin/activate`

### Running Tests
- **All tests**: `.venv/bin/pytest`
- **Single test file**: `.venv/bin/pytest tests/test_domain.py`
- **Single test function**: `.venv/bin/pytest tests/test_domain.py -k test_price_range_validation_and_parameters`
- **Live integration tests** (hits Tecimob API): `.venv/bin/pytest tests/test_live_integration.py`
- **Scripts module verification tests**: `.venv/bin/python scripts/run_tests.py`

### CLI & Verification Utilities
- **Full live research verification**: `.venv/bin/python scripts/verify_research.py`
- **Search rentals**: `.venv/bin/python scripts/run_search.py --city timoteo-mg --bedrooms 2`
- **Search with price constraints**: `.venv/bin/python scripts/run_search.py --city timoteo-mg --max-price 2500`
- **Property detail inspection**: `.venv/bin/python scripts/run_property_detail.py 422`
- **Inspect search facets**: `.venv/bin/python scripts/run_facets.py`

### Linting
- **Check codebase**: `ruff check .`
- **Auto-fix lint issues**: `ruff check --fix .`

## Architecture & Code Structure

The repository maintains two parallel layers sharing domain concepts:

### 1. Core Package (`src/cabralporto_research/`)
Installable Python library structured with explicit collaborator injection:
- `client.py` (`CabralPortoRentalClient`): Top-level facade coordinating the network gateway and parser suite.
- `collaborators.py`: Decouples `RentalNetworkGateway` (HTTP & URL generation) and `RentalParserSuite` (payload deserializers).
- `infrastructure/`:
  - `url_builder.py` (`UrlBuilder`): Translates `SearchCriteria` into Tecimob query strings with nested brackets (`filter[...]`).
  - `http_client.py` (`HttpxHttpClient`): Network transport injecting required headers (`x-domain`).
- `domain/`: Value objects and models (`SearchCriteria`, `RentalListingSummary`, `PropertyDetail`, `PhotoGallery`, `PriceRange`, `RoomCount`).
- `parsers/`: Modular parsers (`search_parser.py`, `detail_parser.py`, `metadata_parser.py`).

### 2. MCP Provider & Calisthenics Adapter (`scripts/`)
Pluggable provider for Central Rental Research MCP servers:
- `providers/cabralporto.py` (`CabralPortoRentalProvider`): Implements `RentalProviderProtocol`.
- `mcp/tools.py` (`CabralPortoMcpAdapter`): Exposes standard FastMCP tool definitions (`cabralporto_search_rentals`, `cabralporto_get_property_detail`, `cabralporto_get_facets`).
- `client/`: Dedicated `http_transport.py` and `query_builder.py` adhering to strict calisthenics.
- `domain/`: Value objects, entities, and first-class collections (`RentalListingCollection`, `FacetCollection`).

#### Object Calisthenics Standards in `scripts/`:
- **Zero `else`**: Early returns, guard clauses, and polymorphism exclusively.
- **Single indent level**: At most 1 indentation level per method.
- **Wrapped primitives**: All domain primitives wrapped in value objects (`ListingPrice`, `PropertyCode`, `RentalFilter`).
- **First-class collections**: Dedicated collection classes without additional state.
- **One dot per line**: Demeter enforcement via intermediate assignments.
- **Entity limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines, ≤ 2 instance variables per class.

### 3. Tecimob Backend API Integration Details
- **Base URL**: `https://api-sites.tecimob.com.br/api/`
- **Authentication**: None required (public tenant endpoints).
- **Mandatory Tenant Header**: `x-domain: cabralportoimoveis.com.br` (maps to agency UUID `7d0672ea-23e6-48d3-a567-6793833cb59a`).
- **Search Endpoint**: `GET /api/properties?custom_query=card&sort={sort}&offset={page}&limit={limit}&filter[...]`
  - Pagination uses 1-indexed `offset={page}` with page size `limit={n}` (default 21).
  - Bedroom query parameter: `filter[by_room_greater_equals][bedroom]={n}` (min) or `filter[by_room_equals][bedroom]={n}` (exact).
  - Price bounds: `filter[by_higher_than_price]={min}`, `filter[by_lower_than_price]={max}`.
- **Detail Endpoint**: `GET /api/properties/{code_or_uuid}` (supports reference code like `422`).
- **Facets Endpoint**: `GET /api/properties/get-facets-count`.

## Reference Documentation Pointers

Detailed specifications and architectural decisions are located in:
- **Single Source of Truth API Spec**: `docs/sot/cabralporto_tecimob_api_spec.md` (complete query parameter matrices and schemas).
- **ADR 0001 Architecture**: `docs/adr/0001-rental-search-mcp-module-design.md` (hexagonal design and provider protocol).
- **cURL & API Recipes**: `docs/api_reference.md`.
- **Reverse Engineering Analysis**: `docs/api-research.md`.
- **Calisthenics Adherence**: `scripts/ARCHITECTURE.md`.
- **MCP Server Usage Guide**: `scripts/USAGE.md`.
