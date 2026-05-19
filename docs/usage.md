# Usage

This SDK wraps the Datalogics `w_create_shipping` endpoint.

## Create a Shipment

```python
from datalogic_sdk import DatalogicClient, Order, Origin, ShippingDetails

client = DatalogicClient("YOUR_AUTHENTICATION_TOKEN")

response = client.create_shipping(
    order=Order(
        id=123,
        number="ORD-123",
        shipping=ShippingDetails(
            street="Herzl",
            city="Tel Aviv",
            first_name="Dana",
            last_name="Cohen",
            postcode="6100000",
            house="10",
            apartment="3",
            email="dana@example.com",
            entrance="B",
            floor="4",
            phone="0501234567",
            n_code="PICKUP_LOCATION_ID",
            extra_fields={"site_code": "SITE-7"},
        ),
        comment="Leave at reception",
        extra_fields={"delivery_time": "16:00-20:00"},
    ),
    origin=Origin(
        contract="1234",
        company_name="Acme Ltd",
        city="Jerusalem",
        street="Jaffa",
        house="1",
        phone="021234567",
        email="ops@example.com",
    ),
)

print(response.status_code)
print(response.data)
```

## Pickup Locations

Set `ShippingDetails.n_code` only when the customer chooses a pickup location.
Use the pickup location ID provided by Datalogics.

## Undocumented Fields

The Datalogics WooCommerce plugin sends a broader order object than the minimal
HTTP example in the vendor docs. If your account uses additional fields such as
site codes or delivery-time selections, pass them through `extra_fields` on
`Order`, `ShippingDetails`, or `Origin`.

Useful implementation references:

- <https://plugins.svn.wordpress.org/datalogics/trunk/>
- <https://plugins.trac.wordpress.org/browser/datalogics/trunk>

Treat those as behavior references for the WooCommerce integration, not as the
formal raw HTTP API contract.

## Errors

```python
from datalogic_sdk import DatalogicAPIError, DatalogicValidationError

try:
    response = client.create_shipping(order=order, origin=origin)
except DatalogicValidationError as exc:
    print(f"Invalid request: {exc}")
except DatalogicAPIError as exc:
    print(f"API error {exc.status_code}: {exc.response_body}")
```

`DatalogicValidationError` means the SDK rejected invalid local input before
making an HTTP request.

`DatalogicAPIError` means the API returned a non-2xx HTTP status or the network
request failed.
