# API Reference

## `DatalogicClient`

```python
DatalogicClient(
    token: str,
    *,
    base_url: str = "https://connect.datalogics.co.il",
    timeout: float = 30.0,
    transport: Transport | None = None,
)
```

Creates a synchronous client for the Datalogics shipping API.

The authentication token is sent in the JSON request body because that is how
the vendor endpoint is documented.

## `create_shipping`

```python
response = client.create_shipping(order=order, origin=origin)
```

Calls:

```text
POST https://connect.datalogics.co.il/rest/w_create_shipping
Content-Type: application/json
```

Returns `DatalogicResponse`.

Raises:

- `DatalogicValidationError` when local input is invalid.
- `DatalogicAPIError` when the API returns a non-2xx response or the network
  request fails.

## Models

### `ShippingDetails`

Required fields:

- `street`
- `city`
- `first_name`
- `last_name`
- `house`
- `phone`

Optional fields:

- `postcode`
- `apartment`
- `email`
- `company`
- `entrance`
- `floor`
- `n_code`
- `extra_fields`

### `Order`

Required fields:

- `id`
- `number`
- `shipping`

Optional fields:

- `comment`
- `extra_fields`

### `Origin`

Required fields:

- `contract`
- `company_name`
- `city`
- `street`
- `house`
- `phone`
- `email`

Validation:

- `contract` must be exactly 4 characters.
- `email` must contain `@`.
- `extra_fields` on all models must be mappings with string keys and
  JSON-serializable values, and cannot override reserved SDK field names.

## `DatalogicResponse`

```python
@dataclass(frozen=True)
class DatalogicResponse:
    status_code: int
    data: Any
    text: str
    headers: Mapping[str, str]
```

`data` contains parsed JSON when the response body is valid JSON. Otherwise it
contains the raw response text. Empty response bodies are returned as `None`.
