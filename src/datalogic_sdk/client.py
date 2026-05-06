"""HTTP client for the Datalogics shipping API."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from datalogic_sdk.exceptions import DatalogicAPIError, DatalogicValidationError
from datalogic_sdk.models import Order, Origin

DEFAULT_BASE_URL = "https://connect.datalogics.co.il"
CREATE_SHIPPING_PATH = "/rest/w_create_shipping"


@dataclass(frozen=True)
class DatalogicResponse:
    """Successful response returned by the Datalogics API."""

    status_code: int
    data: Any
    text: str
    headers: Mapping[str, str]


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    body: bytes
    headers: Mapping[str, str]


class Transport(Protocol):
    def post(
        self,
        url: str,
        *,
        payload: Mapping[str, Any],
        timeout: float,
        headers: Mapping[str, str],
    ) -> TransportResponse:
        """Send a JSON POST request."""
        ...


class UrlLibTransport:
    """Default transport implemented with Python's standard library."""

    def post(
        self,
        url: str,
        *,
        payload: Mapping[str, Any],
        timeout: float,
        headers: Mapping[str, str],
    ) -> TransportResponse:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(url, data=body, headers=dict(headers), method="POST")

        try:
            with urlopen(request, timeout=timeout) as response:
                return TransportResponse(
                    status_code=response.status,
                    body=response.read(),
                    headers=dict(response.headers.items()),
                )
        except HTTPError as exc:
            return TransportResponse(
                status_code=exc.code,
                body=exc.read(),
                headers=dict(exc.headers.items()),
            )
        except URLError as exc:
            raise DatalogicAPIError(
                f"Failed to call Datalogics API: {exc.reason}",
                status_code=0,
                response_body=str(exc.reason),
            ) from exc


class DatalogicClient:
    """Client for Datalogics shipping operations."""

    def __init__(
        self,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        if not isinstance(token, str) or not token.strip():
            raise DatalogicValidationError("token is required")
        if not isinstance(base_url, str) or not base_url.strip():
            raise DatalogicValidationError("base_url is required")
        if timeout <= 0:
            raise DatalogicValidationError("timeout must be greater than 0")

        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = float(timeout)
        self._transport = transport or UrlLibTransport()

    def create_shipping(self, *, order: Order, origin: Origin) -> DatalogicResponse:
        """Create a shipping order.

        Raises:
            DatalogicValidationError: Request data is invalid.
            DatalogicAPIError: The API returns a non-2xx response or networking fails.
        """

        if not isinstance(order, Order):
            raise DatalogicValidationError("order must be an Order instance")
        if not isinstance(origin, Origin):
            raise DatalogicValidationError("origin must be an Origin instance")

        payload = {
            "token": self._token,
            "order": order.to_dict(),
            "origin": origin.to_dict(),
        }

        response = self._transport.post(
            f"{self._base_url}{CREATE_SHIPPING_PATH}",
            payload=payload,
            timeout=self._timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "datalogic-sdk-python/0.1.0",
            },
        )

        text = response.body.decode("utf-8", errors="replace")
        data = self._parse_response_body(text)

        if response.status_code < 200 or response.status_code >= 300:
            raise DatalogicAPIError(
                f"Datalogics API returned HTTP {response.status_code}",
                status_code=response.status_code,
                response_body=text,
            )

        return DatalogicResponse(
            status_code=response.status_code,
            data=data,
            text=text,
            headers=response.headers,
        )

    @staticmethod
    def _parse_response_body(text: str) -> Any:
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
