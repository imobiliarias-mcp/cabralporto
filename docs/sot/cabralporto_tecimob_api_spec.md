# Tecimob Real Estate Platform API Specification — Cabral Porto Imóveis

## 1. Overview & Architecture

This document serves as the **Single Source of Truth (SOT)** for the reverse-engineered rental search and property retrieval APIs powering **Cabral Porto Corretor de Imóveis** (`https://cabralportoimoveis.com.br/`).

### 1.1 Platform Identification
- **SaaS Vendor**: [Tecimob](https://www.tecimob.com.br/) (cloud real estate CMS & CRM engine)
- **Backend Architecture**: Laravel RESTful API (`App\Models\Properties\Property`)
- **API Base URL**: `https://api-sites.tecimob.com.br/api/`
- **Frontend Framework**: Next.js React web application with SSR and CSR
- **Character Encoding**: `application/json; charset=utf-8`
- **Tenant ID**: `7d0672ea-23e6-48d3-a567-6793833cb59a`
- **Asset / Media CDN**:
  - `https://imagens.tecimob.com.br/media/`
  - High-res images: `https://imagens.tecimob.com.br/media/{agency_id}/properties/{property_uuid}/images/{filename}`
  - Thumbnails: `https://imagens.tecimob.com.br/media/{agency_id}/properties/{property_uuid}/images/{width}x{height}/outside/{filename}`

### 1.2 Authentication & Access Control
- **Public Access**: All search queries, filters, property details, and media are publicly accessible without user tokens, passwords, cookies, or CSRF headers.
- **Mandatory Request Headers**:
  - `x-domain: cabralportoimoveis.com.br` (Required for tenant identification)
  - `Accept: application/json`
  - `User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...`

---

## 2. Endpoints Catalog

### 2.1 Property Search & Listings
Searches properties across sales and rentals with full filtering, sorting, and pagination.

- **URL**: `GET https://api-sites.tecimob.com.br/api/properties`
- **Method**: `GET`
- **Headers**: `x-domain: cabralportoimoveis.com.br`
- **Query Parameters**:

| Parameter | Type | Required | Description | Format / Values |
| :--- | :--- | :---: | :--- | :--- |
| `custom_query` | `string` | No | Response format | `card` (optimized for listing view) |
| `filter[transaction]` | `integer` | No | Transaction category | `2` (Aluguel), `1` (Venda) |
| `filter[by_neighborhood_or_city_slug]` | `string` | No | Municipality slug | e.g. `timoteo-mg`, `ipatinga-mg` |
| `filter[by_neighborhood_slug]` | `string` | No | Specific neighborhood | e.g. `timoteo-mg-eldorado` |
| `filter[by_type_or_subtype_slug]` | `string` | No | Property type slug | e.g. `apartamento`, `casa`, `comercial` |
| `filter[by_room_greater_equals][bedroom]` | `integer` | No | Minimum bedrooms | e.g. `1`, `2`, `3` |
| `filter[by_room_equals][bedroom]` | `integer` | No | Exact bedrooms | e.g. `1`, `2`, `3` |
| `filter[by_room_greater_equals][suite]` | `integer` | No | Minimum suites | e.g. `1`, `2` |
| `filter[by_room_greater_equals][garage]` | `integer` | No | Minimum garages | e.g. `1`, `2` |
| `filter[by_higher_than_price]` | `integer` | No | Minimum price in BRL | e.g. `1000` |
| `filter[by_lower_than_price]` | `integer` | No | Maximum price in BRL | e.g. `3000` |
| `filter[by_area][greater_equals]` | `integer` | No | Minimum area in m² | e.g. `50` |
| `filter[by_area][lower_equals]` | `integer` | No | Maximum area in m² | e.g. `250` |
| `filter[by_area][name]` | `string` | No | Area measurement field | `total_area`, `built_area` |
| `sort` | `string` | No | Sort order | `-created_at,id`, `price`, `-price` |
| `offset` | `integer` | No | Page index (1-indexed) | `1`, `2`, `3` (Default: 1) |
| `limit` | `integer` | No | Items per page | `21` (Default: 21) |

- **Response Structure (Paginated)**:
```json
{
  "data": [
    {
      "id": "778af35a-9cf1-4c29-944b-db1cf5947416",
      "code": 422,
      "title": "Apartamento em Eldorado, Timóteo/MG",
      "price": 1400,
      "address": {
        "neighborhood": "Eldorado",
        "city": "Timóteo",
        "state": "MG"
      },
      "rooms": {
        "bedroom": 2,
        "garage": 1
      },
      "area": {
        "total_area": 85.0
      },
      "images": [ ... ]
    }
  ],
  "meta": {
    "pagination": {
      "total": 3,
      "per_page": 21,
      "current_page": 1,
      "total_pages": 1
    }
  }
}
```

### 2.2 Property Detail Retrieval
Retrieves comprehensive property specifications, features, descriptions, and media gallery.

- **URL**: `GET https://api-sites.tecimob.com.br/api/properties/{id_or_code}`
- **Method**: `GET`
- **Headers**: `x-domain: cabralportoimoveis.com.br`
- **Path Parameter**:
  - `{id_or_code}`: Reference code (integer e.g. `422`) or internal UUID (`778af35a-9cf1-4c29-944b-db1cf5947416`).
- **Response Structure**:
```json
{
  "data": {
    "id": "778af35a-9cf1-4c29-944b-db1cf5947416",
    "code": 422,
    "title": "Apartamento em Eldorado, Timóteo/MG",
    "description": "<p>Aluguel de Apartamento no Bairro Eldorado...</p>",
    "price": 1400,
    "total_price": 1400,
    "condominium": 220,
    "address": {
      "neighborhood": "Eldorado",
      "city": "Timóteo",
      "state": "MG",
      "street": "Rua ...",
      "zip_code": "35180-000"
    },
    "rooms": {
      "bedroom": 2,
      "bathroom": 1,
      "garage": 1
    },
    "commodities": [
      { "id": 1, "name": "Garagem", "amount": 1 },
      { "id": 2, "name": "Dormitórios", "amount": 2 }
    ],
    "images": [
      {
        "url": "https://imagens.tecimob.com.br/media/.../cbbf4d2f...ZXmX.jpg",
        "description": "Sala",
        "featured": true
      }
    ]
  }
}
```

### 2.3 Supporting Facet Endpoints

#### Filter States & Cities
- **URL**: `GET https://api-sites.tecimob.com.br/api/filters/states`
- **Headers**: `x-domain: cabralportoimoveis.com.br`
- **Returns**: Hierarchical list of states and cities with available property counts.

#### Filter Neighborhoods
- **URL**: `GET https://api-sites.tecimob.com.br/api/filters/neighborhoods`
- **Headers**: `x-domain: cabralportoimoveis.com.br`
- **Returns**: Available neighborhoods and slug values.

#### Filter Types
- **URL**: `GET https://api-sites.tecimob.com.br/api/filters/types`
- **Headers**: `x-domain: cabralportoimoveis.com.br`
- **Returns**: Property categories and subtypes.

---

## 3. Error Handling & Edge Cases

1. **422 Unprocessable Entity for Missing Property**:
   When requesting a non-existent property code, the API returns:
   ```json
   {
     "message": "Não encontrado.",
     "status_code": 422
   }
   ```
   The client translates HTTP 422 to domain exception `PropertyNotFoundError`.

2. **Rooms Format Inconsistency**:
   - Residential properties: `rooms` is a dictionary (`{"bedroom": 2}`).
   - Commercial / land properties: `rooms` is an empty list (`[]`).
   - Parsers must guard type with `isinstance(data.get("rooms"), dict)`.

3. **IPv6 Host Fallback**:
   Tecimob hosts resolve with dual-stack A/AAAA records. When running on environments without active IPv6 routes, connection attempts time out or fail with `Network is unreachable`. The HTTP client provides an automatic IPv4 socket resolution fallback.
