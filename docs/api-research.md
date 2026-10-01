# Reverse-Engineered API Specification: Cabral Porto Imóveis

## 1. Overview & Architecture

Cabral Porto Corretor de Imóveis (`https://cabralportoimoveis.com.br`) is a real estate agency portal built on top of the **Tecimob** SaaS real estate platform.

The web application utilizes a hybrid architecture:
- **Frontend / Client & SSR**: A **Next.js** web application rendering dynamic search views (`/list`) and property detail pages (`/details` / `/imovel/{slug}/{id}`).
- **Backend API**: A headless RESTful JSON API hosted at `https://api-sites.tecimob.com.br/api/` powered by a Laravel backend (`App\Models\Properties\Property`).
- **CDN & Media Storage**: High-resolution and optimized WebP images hosted on Amazon S3 / Tecimob CDN (`https://imagens.tecimob.com.br/media/...`).

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All property listing searches, filter queries, pagination requests, detail pages, and photo galleries are publicly accessible without authentication tokens, cookies, or CSRF headers.
- **Tenant Identification**: The backend determines the agency tenant via the custom HTTP header:
  ```http
  x-domain: cabralportoimoveis.com.br
  ```
  The agency UUID associated with this domain is `7d0672ea-23e6-48d3-a567-6793833cb59a`.
- **HTTP Methods**: All research operations (search, filter, pagination, detail retrieval, facets) utilize standard `GET` requests.
- **Payload Format**: All responses are JSON with standard UTF-8 encoding.

---

## 2. Canonical Search Routing & URL Mapping

The Next.js frontend maps hierarchical SEO search URLs into queries dispatched to the Tecimob REST API:

### 2.1 Frontend SEO Search Routing
```http
GET /{transaction}/{type}/{address}?typeArea={typeArea}&floorComparision={comp}&sort={sort}&offset={offset}&limit={limit}&bedrooms={bedrooms} HTTP/1.1
Host: cabralportoimoveis.com.br
```

#### Path Segments
| Segment | Type | Example Values | Description |
| :--- | :--- | :--- | :--- |
| `{transaction}` | `string` | `alugar`, `comprar` | Transaction purpose (`alugar` for rentals, `comprar` for sales). |
| `{type}` | `string` | `imoveis`, `apartamento`, `casa`, `comercial`, `lote`, etc. | Property category. Default is `imoveis` (all types). |
| `{address}` | `string` | `timoteo-mg`, `ipatinga-mg`, `coronel-fabriciano-mg` | Municipality slug (or joined with `+` for multiple locations). |

### 2.2 Direct Tecimob REST Search Endpoint
```http
GET /api/properties?custom_query=card&sort={sort}&offset={offset}&limit={limit}&filter[transaction]={transaction_id}&filter[by_neighborhood_or_city_slug]={city_slug}&filter[by_room_greater_equals][bedroom]={bedrooms} HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: cabralportoimoveis.com.br
Accept: application/json
```

---

## 3. Request Parameters & Filter Behavior

The search engine supports rich criteria formatted using nested PHP/Laravel array query notation (`filter[...]`):

| Parameter | Type | Example Values | Tecimob Internal Logic / Description |
| :--- | :--- | :--- | :--- |
| `custom_query` | `string` | `card` | Formats response optimized for property result cards. |
| `filter[transaction]` | `integer` | `2` (Rentals), `1` (Sales) | **Transaction purpose** constraint. |
| `filter[by_neighborhood_or_city_slug]` | `string` | `timoteo-mg`, `ipatinga-mg` | Municipality slug constraint. |
| `filter[by_neighborhood_slug]` | `string` | `timoteo-mg-eldorado` | Specific neighborhood slug filter. |
| `filter[by_type_or_subtype_slug]` | `string` | `apartamento`, `casa`, `comercial` | Property category filter. |
| `filter[by_room_greater_equals][bedroom]` | `integer` | `1`, `2`, `3`, `4` | **Minimum bedrooms** constraint ("N or more"). |
| `filter[by_room_equals][bedroom]` | `integer` | `1`, `2`, `3` | **Exact bedrooms** constraint. |
| `filter[by_room_greater_equals][suite]` | `integer` | `1`, `2` | Minimum suites count. |
| `filter[by_room_greater_equals][garage]` | `integer` | `1`, `2` | Minimum parking spaces. |
| `filter[by_higher_than_price]` | `integer` | `1000` | Minimum rental price in BRL. |
| `filter[by_lower_than_price]` | `integer` | `2500` | Maximum rental price in BRL. |
| `filter[by_area][greater_equals]` | `integer` | `60` | Minimum area in m². |
| `filter[by_area][lower_equals]` | `integer` | `200` | Maximum area in m². |
| `filter[by_area][name]` | `string` | `total_area`, `built_area`, `private_area` | Area dimension to constrain. |
| `filter[by_area][measure]` | `string` | `m²`, `ha` | Unit of measurement. |
| `sort` | `string` | `-created_at,id`, `price`, `-price` | Sorting order (`-created_at,id` for recent, `price` for lowest price). |
| `offset` | `integer` | `1`, `2`, `3`... | **1-indexed page number** (not record offset). |
| `limit` | `integer` | `21`, `10` | Number of listings per page. |

---

## 4. Pagination Behavior

### 4.1 Mechanics
- **Page Parameter**: `offset` specifies the **page number** (1-indexed: `offset=1` is page 1, `offset=2` is page 2).
- **Page Size**: `limit` specifies the page size (default `21` on the website).
- **Response Structure with Pagination**:
  When `offset` or `limit` is provided, the API uses Laravel's `LengthAwarePaginator` and wraps results with a `meta` block:
  ```json
  {
    "data": [ ... ],
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
- **Response Structure without Pagination**:
  When neither `offset` nor `limit` is provided, the API executes an unpaginated query returning `{ "data": [ ... ] }`.

### 4.2 Out-of-Bounds & Termination Behavior
- Requesting an out-of-bounds page (e.g. `offset=999&limit=21`) returns HTTP 200 with an empty `data` array:
  ```json
  {
    "data": [],
    "meta": {
      "pagination": {
        "total": 3,
        "per_page": 21,
        "current_page": 999,
        "total_pages": 1
      }
    }
  }
  ```
- Termination is detected when `len(data) == 0` or when `current_page >= total_pages`.

---

## 5. Property Detail Retrieval

Full property details are accessible directly through the REST API by reference code or UUID, as well as via server-side rendered Next.js pages.

### 5.1 Detail API Endpoint
```http
GET /api/properties/{id_or_reference} HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: cabralportoimoveis.com.br
Accept: application/json
```

- **Reference Lookup**: Requesting `/api/properties/422` immediately resolves property Ref 422 with HTTP 200.
- **UUID Lookup**: Requesting `/api/properties/778af35a-9cf1-4c29-944b-db1cf5947416` also returns the exact property record.
- **Missing Property**: Requesting a non-existent code returns HTTP 422 with:
  ```json
  {
    "error": "No query results for model [App\\Models\\Properties\\Property].",
    "message": "Não encontrado.",
    "status_code": 422
  }
  ```

### 5.2 Property Detail Fields
| Domain Field | JSON Field Path | Example Value |
| :--- | :--- | :--- |
| `id` | `data.id` | `"778af35a-9cf1-4c29-944b-db1cf5947416"` |
| `reference` | `data.reference` | `"422"` |
| `title` | `data.title_formatted` | `"Apartamento em Eldorado, Timóteo/MG"` |
| `price` | `data.price` | `"R$1.400,00"` |
| `total_price` | `data.total_price` | `"R$1.400,00"` |
| `condominium_price` | `data.condominium_price` | `"R$220,00"` |
| `total_taxes_price` | `data.total_taxes_price` | `"R$220,00"` |
| `transaction` | `data.transaction` | `"ALUGUEL"` |
| `status` | `data.status` | `"Disponível"` |
| `neighborhood` | `data.neighborhood_description.name` | `"Eldorado"` |
| `city` | `data.city_description.name` | `"Timóteo"` |
| `formatted_address` | `data.address.formatted` | `"Eldorado - Timóteo/MG"` |
| `bedrooms` | `data.rooms.bedroom.value` | `2` |
| `suites` | `data.rooms.suite.value` | `0` (or `None`) |
| `bathrooms` | `data.rooms.bathroom.value` | `1` |
| `garages` | `data.rooms.garage.value` | `1` |
| `areas` | `data.areas` | `{"built_area": {"title": "Área Construída", "value": "65", "measure": "m²"}}` |
| `description` | `data.description` | HTML description content |
| `photos` | `data.images_extra` | List of photo objects with CDN URLs |

> [!NOTE]
> For commercial properties or land lots without room definitions, `data.rooms` is serialized as an empty list (`[]`) rather than a dictionary. Parsers must check type before attribute access.

---

## 6. Photo Gallery & Media Resolution

Property photos are embedded in `images_extra` within the property detail and search card payloads.

### 6.1 Photo Structure
```json
{
  "id": "cbbf4d2f-2ed8-46cd-8957-b23fc51d0f51",
  "gallery": 1,
  "caption": null,
  "file_url": {
    "large": "https://imagens.tecimob.com.br/media/7d0672ea-23e6-48d3-a567-6793833cb59a/properties/778af35a-9cf1-4c29-944b-db1cf5947416/images/cbbf4d2f-2ed8-46cd-8957-b23fc51d0f511788871843ZXmX.jpg",
    "medium": "https://imagens.tecimob.com.br/media/7d0672ea-23e6-48d3-a567-6793833cb59a/properties/778af35a-9cf1-4c29-944b-db1cf5947416/images/600x450/outside/cbbf4d2f-2ed8-46cd-8957-b23fc51d0f511788871843ZXmX.webp"
  }
}
```

- **Large Image URL**: High-resolution JPEG photo.
- **Medium Image URL**: Optimized WebP thumbnail (600x450).

---

## 7. Supporting Metadata & Facet Endpoints

The following supporting endpoints provide available options for search filters:

| Endpoint | Method | Response Description |
| :--- | :--- | :--- |
| `/filters/states?sort=acronym` | `GET` | List of states and nested active cities (e.g. `timoteo-mg`, `ipatinga-mg`). |
| `/filters/neighborhoods?sort=slug` | `GET` | 50 neighborhood slugs (e.g. `timoteo-mg-eldorado`, `timoteo-mg-centro`). |
| `/filters/types?sort=order&filter[having_properties]=true` | `GET` | Available property types (e.g. `apartamento`, `casa`, `comercial`). |
| `/properties/areas` | `GET` | Supported area metric names and units (`total_area`, `built_area`, `m²`). |
| `/properties/furnitures` | `GET` | Furniture options (`Sem mobília`, `Semi-mobiliado`). |
| `/properties/profiles` | `GET` | Property profiles (`Residencial`, `Comercial`, `Industrial`). |
| `/properties/situations` | `GET` | Property situations (`Usado`, `Em construção`, etc.). |
| `/properties/transactions` | `GET` | Transaction purpose list (`comprar`: 1, `alugar`: 2). |

---

## 8. Target URL Reproduction Analysis

### Target URL from Prompt
`https://cabralportoimoveis.com.br/alugar/imoveis/timoteo-mg?typeArea=total_area&floorComparision=equals&sort=-created_at%2Cid&offset=1&limit=21&bedrooms=2`

### Request Translation
```http
GET /api/properties?custom_query=card&sort=-created_at,id&offset=1&limit=21&filter[transaction]=2&filter[by_neighborhood_or_city_slug]=timoteo-mg&filter[by_room_greater_equals][bedroom]=2&filter[by_area][name]=total_area HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: cabralportoimoveis.com.br
Accept: application/json
```

### Verified Live Results
The query accurately returns all matching rental properties in Timóteo with at least 2 bedrooms:
1. **Ref 422**: *Apartamento em Eldorado, Timóteo/MG* — `R$ 1.400,00` — 2 quartos, 1 banheiro, 1 vaga, 65 m²
2. **Ref 415**: *Apartamento em Bromélias, Timóteo/MG* — `R$ 1.800,00` — 3 quartos, 1 suíte, 1 banheiro, 1 vaga
3. **Ref 196**: *Apartamento para Locação* — `R$ 780,00` — 3 quartos, 1 banheiro, 1 vaga
