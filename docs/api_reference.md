# Cabral Porto Imóveis — API Reference & Quick Recipes

This reference provides ready-to-use cURL recipes, HTTP examples, and parameter references for querying the **Cabral Porto Imóveis** API powered by Tecimob.

---

## 1. Quick Recipes (cURL)

### 1.1 Target Prompt Search (Timóteo, Rentals, 2+ Bedrooms)
```bash
curl -s "https://api-sites.tecimob.com.br/api/properties?custom_query=card&sort=-created_at,id&offset=1&limit=21&filter\[transaction\]=2&filter\[by_neighborhood_or_city_slug\]=timoteo-mg&filter\[by_room_greater_equals\]\[bedroom\]=2" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.2 All Rental Listings in Timóteo
```bash
curl -s "https://api-sites.tecimob.com.br/api/properties?custom_query=card&sort=-created_at,id&offset=1&limit=21&filter\[transaction\]=2&filter\[by_neighborhood_or_city_slug\]=timoteo-mg" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.3 Filtered Search by Price and Bedrooms
```bash
curl -s "https://api-sites.tecimob.com.br/api/properties?custom_query=card&filter\[transaction\]=2&filter\[by_neighborhood_or_city_slug\]=timoteo-mg&filter\[by_room_greater_equals\]\[bedroom\]=2&filter\[by_higher_than_price\]=1000&filter\[by_lower_than_price\]=2000" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.4 Property Detail by Reference Code (e.g. 422)
```bash
curl -s "https://api-sites.tecimob.com.br/api/properties/422" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.5 Property Detail by UUID
```bash
curl -s "https://api-sites.tecimob.com.br/api/properties/778af35a-9cf1-4c29-944b-db1cf5947416" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.6 Available Cities & States Facet
```bash
curl -s "https://api-sites.tecimob.com.br/api/filters/states" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.7 Available Neighborhoods Facet
```bash
curl -s "https://api-sites.tecimob.com.br/api/filters/neighborhoods" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

### 1.8 Property Types Facet
```bash
curl -s "https://api-sites.tecimob.com.br/api/filters/types" \
  -H "x-domain: cabralportoimoveis.com.br" \
  -H "Accept: application/json"
```

---

## 2. Parameter Reference Matrix

| Parameter | Type | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `x-domain` *(Header)* | `string` | `cabralportoimoveis.com.br` | Tenant identification header. |
| `custom_query` | `string` | `card` | Compact listing card response format. |
| `filter[transaction]` | `int` | `1` (Sale), `2` (Rental) | Transaction purpose. |
| `filter[by_neighborhood_or_city_slug]` | `string` | `timoteo-mg`, `ipatinga-mg` | City or neighborhood slug filter. |
| `filter[by_neighborhood_slug]` | `string` | `timoteo-mg-eldorado` | Specific neighborhood slug. |
| `filter[by_type_or_subtype_slug]` | `string` | `apartamento`, `casa`, `comercial` | Property category filter. |
| `filter[by_room_greater_equals][bedroom]` | `int` | `1`, `2`, `3`... | Minimum bedrooms constraint. |
| `filter[by_room_equals][bedroom]` | `int` | `1`, `2`, `3`... | Exact bedrooms constraint. |
| `filter[by_room_greater_equals][suite]` | `int` | `1`, `2`... | Minimum suites constraint. |
| `filter[by_room_greater_equals][garage]` | `int` | `1`, `2`... | Minimum parking spaces constraint. |
| `filter[by_higher_than_price]` | `int` | e.g. `1000` | Minimum price in BRL. |
| `filter[by_lower_than_price]` | `int` | e.g. `3000` | Maximum price in BRL. |
| `filter[by_area][greater_equals]` | `int` | e.g. `50` | Minimum area in m². |
| `filter[by_area][lower_equals]` | `int` | e.g. `200` | Maximum area in m². |
| `filter[by_area][name]` | `string` | `total_area`, `built_area` | Area measurement type. |
| `sort` | `string` | `-created_at,id`, `price`, `-price` | Sorting order. |
| `offset` | `int` | `1`, `2`, `3`... | Page index (1-indexed). |
| `limit` | `int` | `1`..`50` (default: `21`) | Page size. |

## 3. Public Property Links

Search payloads provide a public property path in `url`. The client resolves relative and
protocol-relative links against the configured public site origin and serializes the same
absolute HTTP(S) destination as both `url` and the legacy `detail_url` field. Valid links
use the documented `/imovel/...` or `/details/...` property routes; search pages, Tecimob
API endpoints, media files, and missing links raise a contextual `ValueError`. Search does
not issue a detail request just to discover a property URL.

Example serialized fields:

```json
{
  "url": "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422",
  "detail_url": "https://cabralportoimoveis.com.br/imovel/apartamento-eldorado/422"
}
```
