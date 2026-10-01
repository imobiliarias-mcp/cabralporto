# Cabral Porto Imóveis — Rental API Reverse Engineering Documentation

Welcome to the reverse-engineering and architecture documentation for **Cabral Porto Corretor de Imóveis** (`https://cabralportoimoveis.com.br/`).

This repository contains the reverse-engineered API specifications, architectural decision records, and clean, modular Python components designed for integration into a **Central Rental Research MCP (Model Context Protocol)** server.

---

## Documentation Structure

- **[Single Source of Truth API Specification](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/docs/sot/cabralporto_tecimob_api_spec.md)** (`docs/sot/cabralporto_tecimob_api_spec.md`):
  Comprehensive contract specification for all endpoints, headers, payload schemas, query matrices, and error handling rules.

- **[Architecture Decision Record 0001](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`):
  Detailed rationale on Ports-and-Adapters (Hexagonal) architecture, SOLID principles, Design Patterns, and strict Object Calisthenics enforcement.

- **[API Reference & Quick Recipes](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/docs/api_reference.md)** (`docs/api_reference.md`):
  Developer reference featuring ready-to-run `curl` commands, parameter dictionaries, and implementation recipes.

- **[Reverse Engineering Analysis](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/docs/api-research.md)** (`docs/api-research.md`):
  Primary research notes, routing mechanics, JSON payload schemas, and Tecimob SaaS platform analysis.

- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/scripts/research-plan.md)** (`scripts/research-plan.md`):
  Detailed research plan, methodology, live verification log, and integration instructions.

- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/cabralporto/scripts/README.md)** (`scripts/README.md`):
  Developer guide for running the Python modules, CLI utilities, and MCP tool handlers.

---

## Key Technical Discoveries Summary

| Dimension | Discovery |
| :--- | :--- |
| **Underlying Platform** | Tecimob SaaS (Headless real estate CMS & CRM) |
| **Backend REST API** | `https://api-sites.tecimob.com.br/api/` (Laravel backend) |
| **Tenant Routing Header** | `x-domain: cabralportoimoveis.com.br` |
| **Tenant Agency UUID** | `7d0672ea-23e6-48d3-a567-6793833cb59a` |
| **Search Route** | `GET /api/properties?custom_query=card&sort={sort}&offset={page}&limit={per_page}&filter[...]` |
| **Room Parameter Encoding** | `filter[by_room_greater_equals][bedroom]={n}`, `filter[by_room_equals][bedroom]={n}` |
| **Numeric Filters** | `filter[by_higher_than_price]`, `filter[by_lower_than_price]`, `filter[by_area][...]` |
| **Pagination Model** | 1-indexed page via `offset={page}`, page size via `limit={n}` (default: 21) |
| **Property Detail Endpoint** | `GET /api/properties/{id_or_code}` by reference code (`422`) or UUID |
| **Media Delivery** | High-res & WebP images from `https://imagens.tecimob.com.br/media/...` |
| **Authentication Requirement** | **None** (Public search, filter, and detail views) |
