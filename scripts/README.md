# Central Rental Research MCP — Cabral Porto Imóveis Module

This package implements the **Cabral Porto Imóveis** rental search provider designed as a plug-and-play adapter for a **Central Rental Research MCP (Model Context Protocol)** server.

---

## 1. Architectural Highlights

- **SOLID Principles**: Single responsibility classes, interface segregation, dependency inversion.
- **Strict Object Calisthenics**:
  - One indent level per method.
  - Zero `else` keywords (guard clauses and early returns only).
  - Wrapped primitives (Value Objects for prices, coordinates, filters, codes).
  - First-class collections (`RentalListingCollection`, `FacetCollection`, `RentalSearchResult`).
  - One dot per line (intermediate assigned variables).
  - No abbreviations.
  - Entity size limits: functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines.
  - ≤ 2 instance variables per class.
  - Tell, Don't Ask encapsulation.
- **Design Patterns**: Adapter, Strategy, Builder, Value Object, First-Class Collection, Factory.
- **Fail Fast**: Immediate boundary validation on inputs, raising descriptive typed domain exceptions.

---

## 2. Directory Layout

```text
scripts/
├── README.md               # Package overview and developer instructions
├── ARCHITECTURE.md         # Calisthenics & SOLID design adherence documentation
├── USAGE.md                # Usage examples and MCP integration guide
├── research-plan.md        # Comprehensive reverse-engineering research plan & logs
├── verify_research.py      # Standalone verification runner
├── __init__.py             # Package marker
├── domain/                 # Pure domain layer
│   ├── __init__.py
│   ├── exceptions.py       # Domain exception hierarchy
│   ├── value_objects.py    # Immutable value objects (Price, Filter, Coordinates)
│   ├── entities.py         # Domain models (RentalListing, RentalPropertyDetail)
│   ├── criteria.py         # Search criteria and filter constraints
│   └── collections.py      # First-class collections (RentalListingCollection, etc.)
├── interfaces/             # Port contracts (MCP Provider Protocols)
│   ├── __init__.py
│   └── provider.py         # RentalProviderProtocol interface
├── client/                 # Infrastructure & Tecimob HTTP client
│   ├── __init__.py
│   ├── configuration.py    # Cabral Porto portal configuration
│   ├── http_transport.py   # Resilient IPv4 HTTP transport with x-domain header
│   ├── query_builder.py    # Filter-to-query translator
│   └── parsers.py          # Response parsers
├── providers/              # Adapter layer
│   ├── __init__.py
│   └── cabralporto.py      # CabralPortoRentalProvider implementation
├── mcp/                    # MCP tool contracts & handlers
│   ├── __init__.py
│   └── tools.py            # Central Rental Research MCP tools
├── run_search.py           # CLI tool to run rental searches
├── run_property_detail.py  # CLI tool to fetch full property details
├── run_facets.py           # CLI tool to list search facets
└── run_tests.py            # Full test suite runner
```

---

## 3. Quick Start

### 3.1 Verification Runner
Verify all endpoints and target search reproduction:
```bash
python scripts/verify_research.py
```

### 3.2 Search CLI
Search rental listings:
```bash
python scripts/run_search.py --city timoteo-mg --bedrooms 2
```

### 3.3 Property Details CLI
Fetch details for reference code 422:
```bash
python scripts/run_property_detail.py 422
```

### 3.4 Facets CLI
List available cities and neighborhoods:
```bash
python scripts/run_facets.py
```

### 3.5 Run Verification Tests
```bash
python scripts/run_tests.py
```
