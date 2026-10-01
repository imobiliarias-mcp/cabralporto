# Central Rental Research MCP — Usage Guide (Cabral Porto Imóveis)

This guide illustrates how to use the Cabral Porto Imóveis rental search module both as a standalone library and as an MCP (Model Context Protocol) tool provider.

---

## 1. Python API Usage

### 1.1 Basic Search
```python
from scripts.providers.cabralporto import CabralPortoRentalProvider
from scripts.domain.criteria import RentalFilter

provider = CabralPortoRentalProvider.create_default()

# Search all rentals in Timóteo
search_result = provider.search_rentals(RentalFilter().with_city("timoteo-mg"))
print(f"Total found: {search_result.total_count()}")

for listing in search_result.listings():
    print(listing.format_summary())
```

### 1.2 Filtered Search (Target Prompt Equivalent)
```python
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice

# Search 2+ bedroom rentals in Timóteo under R$ 2,500/month
criteria = (
    RentalFilter()
    .with_city("timoteo-mg")
    .with_bedrooms(2)
    .with_price_ceiling(ListingPrice(2500.0))
)

result = provider.search_rentals(criteria)
print(f"Matching listings: {result.total_count()}")
for item in result.listings():
    print(item.format_summary())
```

### 1.3 Fetch Property Details
```python
from scripts.domain.value_objects import PropertyCode

# Look up property by reference code
code = PropertyCode("422")
detail = provider.get_property_detail(code)
print(detail.format_detailed_view())
```

### 1.4 Inspect Available Facets (Cities, Neighborhoods, Types)
```python
facets = provider.get_facets()
print("Cities:", facets.city_names())
print("Neighborhoods:", facets.neighborhood_names())
```

---

## 2. Integrating with a Central Rental Research MCP Server

### 2.1 FastMCP Integration
```python
from mcp.server.fastmcp import FastMCP
from scripts.mcp.tools import CabralPortoMcpAdapter
from scripts.providers.cabralporto import CabralPortoRentalProvider

mcp = FastMCP("Rental Research Center")
provider = CabralPortoRentalProvider.create_default()
adapter = CabralPortoMcpAdapter(provider)

@mcp.tool()
def search_cabralporto_rentals(
    city: str = "timoteo-mg",
    bedrooms: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
) -> dict:
    """Search rental listings from Cabral Porto Imóveis."""
    return adapter.search_rentals_tool(
        city=city,
        bedrooms=bedrooms,
        min_price=min_price,
        max_price=max_price,
        page=page,
    )

@mcp.tool()
def get_cabralporto_property_detail(property_code: str) -> dict:
    """Retrieve full property details and photo gallery by reference code."""
    return adapter.get_property_detail_tool(property_code)

@mcp.tool()
def get_cabralporto_facets() -> dict:
    """Retrieve available filter facets (cities, neighborhoods, property types)."""
    return adapter.get_facets_tool()
```

---

## 3. CLI Runner Scripts

The repository includes ready-to-run CLI scripts:

### 3.1 Verification Runner
Runs live sanity checks against all endpoints:
```bash
python scripts/verify_research.py
```

### 3.2 Property Search CLI
```bash
# Search rentals in Timóteo with 2+ bedrooms
python scripts/run_search.py --city timoteo-mg --bedrooms 2

# Search with price limits
python scripts/run_search.py --city timoteo-mg --min-price 1000 --max-price 2000
```

### 3.3 Property Details CLI
```bash
python scripts/run_property_detail.py 422
```

### 3.4 Filter Facets CLI
```bash
python scripts/run_facets.py
```

### 3.5 Automated Test Suite
```bash
python scripts/run_tests.py
```
