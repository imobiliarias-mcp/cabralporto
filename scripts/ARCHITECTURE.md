# Central Rental Research MCP Architecture & Design Standards — Cabral Porto Imóveis

## 1. Context: Central Rental Research MCP

The **Central Rental Research MCP** aims to unify rental search capabilities across diverse real estate sources (regional portals, agency systems, multi-listing services).

To achieve seamless pluggability, each real estate provider is developed as an isolated module exposing a uniform contract (`RentalProviderProtocol`). The **Cabral Porto Imóveis** module integrates with the underlying **Tecimob SaaS REST Engine** while presenting a domain model completely agnostic of Tecimob's internal quirks.

---

## 2. Object Calisthenics Compliance

Every file and class in this codebase adheres strictly to the 9 rules of Object Calisthenics:

### Rule 1: Only One Level of Indentation per Method
Methods never nest loops inside conditionals or conditionals inside loops. Complex logic is broken down into concise, single-purpose helper methods.

### Rule 2: Don't Use the `else` Keyword
The `else` keyword is strictly prohibited. Guard clauses with early returns and polymorphic handlers handle branching without `else` branches. Across the entire `scripts/` package, there are **0 occurrences** of the `else` keyword.

### Rule 3: Wrap All Primitives and Strings
Domain concepts are represented as strongly-typed Value Objects:
- `ListingPrice`: Validates non-negative currency amounts in BRL.
- `PropertyCode`: Validates non-empty string reference codes.
- `GeoCoordinate`: Validates latitude (-90 to +90) and longitude (-180 to +180).
- `RentalFilter`: Validates search criteria (e.g. `min_price <= max_price`).
- `PriceRange`, `LocationCriteria`, `SpecificationCriteria`, `SearchPagination`.

### Rule 4: First-Class Collections
Any class holding a collection contains no other instance variables. Collections are wrapped in dedicated domain classes:
- `RentalListingCollection`: Wraps `tuple[RentalListing, ...]`.
- `FacetCollection`: Wraps facet groups (`cities`, `neighborhoods`, `types`).
- `RentalSearchResult`: Encapsulates collection and total remote matching count.

### Rule 5: One Dot per Line
Chaining multiple method calls (e.g. `obj.a().b().c()`) violates the Law of Demeter. Intermediate variables are explicitly assigned on their own lines.

### Rule 6: Don't Abbreviate
All symbols use descriptive, clear names. Abbreviations such as `res`, `req`, `mgr`, `btn`, `val`, `cur` are avoided in favor of `response`, `request`, `manager`, `button`, `value`, `cursor`.

### Rule 7: Keep All Entities Small
Strict size ceilings:
- Functions and methods: **≤ 15 lines**.
- Classes: **≤ 100 lines**.
- Modules / files: **< 200 lines**.

### Rule 8: No Classes with More Than 2 Instance Variables
Classes declare at most 2 member attributes. Classes with richer state decompose into focused composite value objects or collaborator bundles.

### Rule 9: No Getters / Setters / Properties Exposing Raw State (Tell, Don't Ask)
Objects expose behaviors and formatting methods (`format_brl()`, `format_summary()`, `to_dictionary()`), rather than acting as passive data bags.

---

## 3. SOLID Principles Compliance

1. **Single Responsibility (SRP)**:
   - `CabralPortoHttpTransport`: HTTP client and header management.
   - `RentalQueryBuilder`: Query parameter compilation and nested filter mapping.
   - `SearchResultParser`: Search listing card JSON deserialization and domain conversion.
   - `PropertyDetailParser`: Property detail and amenities parsing.
   - `CabralPortoRentalProvider`: Provider facade coordinating transport, query building, and parsing.

2. **Open / Closed (OCP)**:
   - Behavior can be extended through interfaces (`RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`) without modifying existing core logic.

3. **Liskov Substitution (LSP)**:
   - `CabralPortoRentalProvider` satisfies `RentalProviderProtocol` completely; any consumer expecting the protocol can use it interchangeably with other agency providers.

4. **Interface Segregation (ISP)**:
   - Separate, fine-grained capability protocols (`RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`) allow clients to depend only on the operations they require.

5. **Dependency Inversion (DIP)**:
   - High-level MCP adapters depend on capability protocols rather than concrete provider implementations.
   - Providers receive collaborators (`HttpTransport`, `QueryBuilder`) injected during construction.

---

## 4. MCP Tool Adapter

The MCP layer in `scripts/mcp/tools.py` exposes standard tool signatures suitable for Model Context Protocol servers:
- `cabralporto_search_rentals`: Search rental listings with filters.
- `cabralporto_get_property_detail`: Retrieve property details by code or UUID.
- `cabralporto_get_facets`: Retrieve available cities, neighborhoods, and types.
