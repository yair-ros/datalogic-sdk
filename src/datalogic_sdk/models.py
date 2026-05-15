"""Request models for the Datalogics shipping API."""

from __future__ import annotations

import json
from collections.abc import Mapping
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


def _optional_extra_fields(
    value: Mapping[str, Any] | None,
    field_name: str,
    *,
    reserved_keys: set[str],
) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise DatalogicValidationError(f"{field_name} must be a mapping when provided")

    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise DatalogicValidationError(f"{field_name} keys must be non-empty strings")
        if key in reserved_keys:
            raise DatalogicValidationError(f"{field_name} cannot override reserved key '{key}'")
        normalized[key] = item

    try:
        json.dumps(normalized, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise DatalogicValidationError(
            f"{field_name} must contain JSON-serializable values"
        ) from exc

    return normalized


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
    email: str | None = None
    company: str | None = None
    entrance: str | None = None
    floor: str | None = None
    n_code: str | None = None
    extra_fields: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "street": _require_text(self.street, "order.shipping.street"),
            "city": _require_text(self.city, "order.shipping.city"),
            "first_name": _require_text(self.first_name, "order.shipping.first_name"),
            "last_name": _require_text(self.last_name, "order.shipping.last_name"),
            "postcode": _optional_text(self.postcode, "order.shipping.postcode"),
            "house": _require_text(self.house, "order.shipping.house"),
            "apartment": _optional_text(self.apartment, "order.shipping.apartment"),
            "email": _optional_text(self.email, "order.shipping.email"),
            "company": _optional_text(self.company, "order.shipping.company"),
            "entrance": _optional_text(self.entrance, "order.shipping.entrance"),
            "floor": _optional_text(self.floor, "order.shipping.floor"),
            "phone": _require_text(self.phone, "order.shipping.phone"),
            "n_code": _optional_text(self.n_code, "order.shipping.n_code"),
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        payload.update(
            _optional_extra_fields(
                self.extra_fields,
                "order.shipping.extra_fields",
                reserved_keys=set(payload),
            )
        )
        return payload


@dataclass(frozen=True)
class Order:
    """Shipping order details."""

    id: int | str
    number: int | str
    shipping: ShippingDetails
    comment: str | None = None
    extra_fields: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        if not isinstance(self.shipping, ShippingDetails):
            raise DatalogicValidationError("order.shipping must be a ShippingDetails instance")

        payload = {
            "id": _require_order_value(self.id, "order.id"),
            "number": _require_order_value(self.number, "order.number"),
            "shipping": self.shipping.to_dict(),
            "comment": _optional_text(self.comment, "order.comment"),
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        payload.update(
            _optional_extra_fields(
                self.extra_fields,
                "order.extra_fields",
                reserved_keys=set(payload),
            )
        )
        return payload


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
    extra_fields: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        contract = _require_text(self.contract, "origin.contract")
        if len(contract) != 4:
            raise DatalogicValidationError("origin.contract must be exactly 4 characters")

        email = _require_text(self.email, "origin.email")
        if "@" not in email:
            raise DatalogicValidationError("origin.email must be a valid email address")

        payload = {
            "contract": contract,
            "company_name": _require_text(self.company_name, "origin.company_name"),
            "city": _require_text(self.city, "origin.city"),
            "street": _require_text(self.street, "origin.street"),
            "house": _require_text(self.house, "origin.house"),
            "phone": _require_text(self.phone, "origin.phone"),
            "email": email,
        }
        payload.update(
            _optional_extra_fields(
                self.extra_fields,
                "origin.extra_fields",
                reserved_keys=set(payload),
            )
        )
        return payload
