"""Request models for the Datalogics shipping API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from datalogic_sdk.exceptions import DatalogicValidationError


def _require_text(value: str | None, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DatalogicValidationError(f"{field_name} is required")
    return value


def _require_order_value(value: int | str, field_name: str) -> int | str:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        return value
    raise DatalogicValidationError(f"{field_name} is required")


def _optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DatalogicValidationError(f"{field_name} must be a non-empty string when provided")
    return value


@dataclass(frozen=True)
class ShippingDetails:
    """Destination details for an order shipment."""

    street: str
    city: str
    first_name: str
    last_name: str
    house: str
    phone: str
    postcode: str | None = None
    apartment: str | None = None
    n_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "street": _require_text(self.street, "order.shipping.street"),
            "city": _require_text(self.city, "order.shipping.city"),
            "first_name": _require_text(self.first_name, "order.shipping.first_name"),
            "last_name": _require_text(self.last_name, "order.shipping.last_name"),
            "postcode": _optional_text(self.postcode, "order.shipping.postcode"),
            "house": _require_text(self.house, "order.shipping.house"),
            "apartment": _optional_text(self.apartment, "order.shipping.apartment"),
            "phone": _require_text(self.phone, "order.shipping.phone"),
            "n_code": _optional_text(self.n_code, "order.shipping.n_code"),
        }
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(frozen=True)
class Order:
    """Shipping order details."""

    id: int | str
    number: int | str
    shipping: ShippingDetails
    comment: str | None = None

    def to_dict(self) -> dict[str, Any]:
        if not isinstance(self.shipping, ShippingDetails):
            raise DatalogicValidationError("order.shipping must be a ShippingDetails instance")

        payload = {
            "id": _require_order_value(self.id, "order.id"),
            "number": _require_order_value(self.number, "order.number"),
            "shipping": self.shipping.to_dict(),
            "comment": _optional_text(self.comment, "order.comment"),
        }
        return {key: value for key, value in payload.items() if value is not None}


@dataclass(frozen=True)
class Origin:
    """Origin settings for a shipping order."""

    contract: str
    company_name: str
    city: str
    street: str
    house: str
    phone: str
    email: str

    def to_dict(self) -> dict[str, Any]:
        contract = _require_text(self.contract, "origin.contract")
        if len(contract) != 4:
            raise DatalogicValidationError("origin.contract must be exactly 4 characters")

        email = _require_text(self.email, "origin.email")
        if "@" not in email:
            raise DatalogicValidationError("origin.email must be a valid email address")

        return {
            "contract": contract,
            "company_name": _require_text(self.company_name, "origin.company_name"),
            "city": _require_text(self.city, "origin.city"),
            "street": _require_text(self.street, "origin.street"),
            "house": _require_text(self.house, "origin.house"),
            "phone": _require_text(self.phone, "origin.phone"),
            "email": email,
        }
