import unittest

from datalogic_sdk import (
    DatalogicAPIError,
    DatalogicClient,
    DatalogicValidationError,
    Order,
    Origin,
    ShippingDetails,
)
from datalogic_sdk.client import TransportResponse


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, *, payload, timeout, headers):
        self.calls.append(
            {
                "url": url,
                "payload": payload,
                "timeout": timeout,
                "headers": headers,
            }
        )
        return self.response


def valid_order():
    return Order(
        id=123,
        number="ORD-123",
        shipping=ShippingDetails(
            street="Herzl",
            city="Tel Aviv",
            first_name="Dana",
            last_name="Cohen",
            house="10",
            apartment="3",
            email="dana@example.com",
            entrance="B",
            floor="4",
            phone="0501234567",
            n_code="PICKUP-1",
            extra_fields={"site_code": "SITE-7"},
        ),
        comment="Leave at reception",
        extra_fields={"delivery_time": "16:00-20:00"},
    )


def valid_origin():
    return Origin(
        contract="1234",
        company_name="Acme",
        city="Jerusalem",
        street="Jaffa",
        house="1",
        phone="021234567",
        email="ops@example.com",
    )


class DatalogicClientTests(unittest.TestCase):
    def test_create_shipping_posts_expected_payload(self):
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body=b'{"success": true, "barcode": "ABC"}',
                headers={"Content-Type": "application/json"},
            )
        )
        client = DatalogicClient("token-123", transport=transport)

        response = client.create_shipping(order=valid_order(), origin=valid_origin())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["barcode"], "ABC")
        self.assertEqual(len(transport.calls), 1)
        call = transport.calls[0]
        self.assertEqual(call["url"], "https://connect.datalogics.co.il/rest/w_create_shipping")
        self.assertEqual(call["headers"]["Content-Type"], "application/json")
        self.assertEqual(call["payload"]["token"], "token-123")
        self.assertEqual(call["payload"]["order"]["shipping"]["n_code"], "PICKUP-1")
        self.assertEqual(call["payload"]["order"]["shipping"]["email"], "dana@example.com")
        self.assertEqual(call["payload"]["order"]["shipping"]["entrance"], "B")
        self.assertEqual(call["payload"]["order"]["shipping"]["floor"], "4")
        self.assertEqual(call["payload"]["order"]["shipping"]["site_code"], "SITE-7")
        self.assertEqual(call["payload"]["order"]["delivery_time"], "16:00-20:00")
        self.assertEqual(call["payload"]["origin"]["contract"], "1234")

    def test_optional_none_fields_are_omitted(self):
        order = Order(
            id=123,
            number=456,
            shipping=ShippingDetails(
                street="Herzl",
                city="Tel Aviv",
                first_name="Dana",
                last_name="Cohen",
                house="10",
                phone="0501234567",
            ),
        )
        transport = FakeTransport(TransportResponse(status_code=200, body=b"{}", headers={}))
        client = DatalogicClient("token-123", transport=transport)

        client.create_shipping(order=order, origin=valid_origin())

        payload = transport.calls[0]["payload"]
        self.assertNotIn("comment", payload["order"])
        self.assertNotIn("postcode", payload["order"]["shipping"])
        self.assertNotIn("apartment", payload["order"]["shipping"])
        self.assertNotIn("email", payload["order"]["shipping"])
        self.assertNotIn("company", payload["order"]["shipping"])
        self.assertNotIn("entrance", payload["order"]["shipping"])
        self.assertNotIn("floor", payload["order"]["shipping"])
        self.assertNotIn("n_code", payload["order"]["shipping"])

    def test_extra_fields_cannot_override_reserved_keys(self):
        order = Order(
            id=123,
            number=456,
            shipping=ShippingDetails(
                street="Herzl",
                city="Tel Aviv",
                first_name="Dana",
                last_name="Cohen",
                house="10",
                phone="0501234567",
                extra_fields={"street": "Other"},
            ),
        )
        client = DatalogicClient("token-123", transport=FakeTransport(None))

        with self.assertRaises(DatalogicValidationError):
            client.create_shipping(order=order, origin=valid_origin())

    def test_contract_must_be_four_characters(self):
        origin = Origin(
            contract="12345",
            company_name="Acme",
            city="Jerusalem",
            street="Jaffa",
            house="1",
            phone="021234567",
            email="ops@example.com",
        )
        client = DatalogicClient("token-123", transport=FakeTransport(None))

        with self.assertRaises(DatalogicValidationError):
            client.create_shipping(order=valid_order(), origin=origin)

    def test_non_success_response_raises_api_error(self):
        transport = FakeTransport(
            TransportResponse(status_code=400, body=b'{"error": "bad request"}', headers={})
        )
        client = DatalogicClient("token-123", transport=transport)

        with self.assertRaises(DatalogicAPIError) as context:
            client.create_shipping(order=valid_order(), origin=valid_origin())

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("bad request", context.exception.response_body)


if __name__ == "__main__":
    unittest.main()
