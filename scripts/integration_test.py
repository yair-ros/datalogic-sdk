from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from datalogic_sdk import DatalogicAPIError, DatalogicClient, Order, Origin, ShippingDetails

ENV_FILE = Path(__file__).with_name("integration_test.env")
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_RESET = "\033[0m"
PLACEHOLDER_VALUES = {
    "DATALOGIC_TOKEN": {"YOUR_TOKEN"},
    "DATALOGIC_SHIPPING_STREET": {"DESTINATION_STREET"},
    "DATALOGIC_SHIPPING_CITY": {"DESTINATION_CITY"},
    "DATALOGIC_ORIGIN_COMPANY_NAME": {"YOUR_COMPANY"},
    "DATALOGIC_ORIGIN_CITY": {"ORIGIN_CITY"},
    "DATALOGIC_ORIGIN_STREET": {"ORIGIN_STREET"},
    "DATALOGIC_ORIGIN_EMAIL": {"ops@example.com"},
}


@dataclass(frozen=True)
class Config:
    token: str
    order_id: str
    order_number: str
    shipping_street: str
    shipping_city: str
    shipping_first_name: str
    shipping_last_name: str
    shipping_house: str
    shipping_phone: str
    origin_contract: str
    origin_company_name: str
    origin_city: str
    origin_street: str
    origin_house: str
    origin_phone: str
    origin_email: str
    shipping_postcode: str | None
    shipping_apartment: str | None
    shipping_n_code: str | None
    order_comment: str | None


def load_config() -> Config:
    values = load_env_file(ENV_FILE)
    require_confirmation(values)
    return Config(
        token=required_value(values, "DATALOGIC_TOKEN"),
        order_id=required_value(values, "DATALOGIC_ORDER_ID"),
        order_number=required_value(values, "DATALOGIC_ORDER_NUMBER"),
        shipping_street=required_value(values, "DATALOGIC_SHIPPING_STREET"),
        shipping_city=required_value(values, "DATALOGIC_SHIPPING_CITY"),
        shipping_first_name=required_value(values, "DATALOGIC_SHIPPING_FIRST_NAME"),
        shipping_last_name=required_value(values, "DATALOGIC_SHIPPING_LAST_NAME"),
        shipping_house=required_value(values, "DATALOGIC_SHIPPING_HOUSE"),
        shipping_phone=required_value(values, "DATALOGIC_SHIPPING_PHONE"),
        origin_contract=required_value(values, "DATALOGIC_ORIGIN_CONTRACT"),
        origin_company_name=required_value(values, "DATALOGIC_ORIGIN_COMPANY_NAME"),
        origin_city=required_value(values, "DATALOGIC_ORIGIN_CITY"),
        origin_street=required_value(values, "DATALOGIC_ORIGIN_STREET"),
        origin_house=required_value(values, "DATALOGIC_ORIGIN_HOUSE"),
        origin_phone=required_value(values, "DATALOGIC_ORIGIN_PHONE"),
        origin_email=required_value(values, "DATALOGIC_ORIGIN_EMAIL"),
        shipping_postcode=optional_value(values, "DATALOGIC_SHIPPING_POSTCODE"),
        shipping_apartment=optional_value(values, "DATALOGIC_SHIPPING_APARTMENT"),
        shipping_n_code=optional_value(values, "DATALOGIC_SHIPPING_N_CODE"),
        order_comment=optional_value(values, "DATALOGIC_ORDER_COMMENT"),
    )


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        print(f"Missing local config: {path}")
        print("Create it from scripts/integration_test.env.example and fill your real values.")
        raise SystemExit(2)

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")
        if not separator:
            raise SystemExit(f"Invalid line in {path}: {raw_line}")

        cleaned = value.strip()
        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
            cleaned = cleaned[1:-1]
        values[key.strip()] = cleaned

    return values


def require_confirmation(values: dict[str, str]) -> None:
    if values.get("DATALOGIC_CONFIRM_REAL_API_CALL") == "yes":
        return

    print("This script calls the real Datalogics API and may create a real shipment.")
    print(f"Edit {ENV_FILE.name} and set DATALOGIC_CONFIRM_REAL_API_CALL=yes to run it.")
    raise SystemExit(2)


def required_value(values: dict[str, str], key: str) -> str:
    value = values.get(key, "").strip()
    if not value:
        raise SystemExit(f"Missing required value in {ENV_FILE.name}: {key}")

    placeholders = PLACEHOLDER_VALUES.get(key, set())
    if value in placeholders:
        raise SystemExit(f"Placeholder value still present in {ENV_FILE.name}: {key}={value}")

    return value


def optional_value(values: dict[str, str], key: str) -> str | None:
    value = values.get(key, "").strip()
    if value:
        return value
    return None


def main() -> None:
    config = load_config()
    confirm_real_api_call(config)
    client = DatalogicClient(config.token)

    order = Order(
        id=config.order_id,
        number=config.order_number,
        shipping=ShippingDetails(
            street=config.shipping_street,
            city=config.shipping_city,
            first_name=config.shipping_first_name,
            last_name=config.shipping_last_name,
            postcode=config.shipping_postcode,
            house=config.shipping_house,
            apartment=config.shipping_apartment,
            phone=config.shipping_phone,
            n_code=config.shipping_n_code,
        ),
        comment=config.order_comment,
    )
    origin = Origin(
        contract=config.origin_contract,
        company_name=config.origin_company_name,
        city=config.origin_city,
        street=config.origin_street,
        house=config.origin_house,
        phone=config.origin_phone,
        email=config.origin_email,
    )

    try:
        response = client.create_shipping(order=order, origin=origin)
    except DatalogicAPIError as exc:
        print(f"API error: HTTP {exc.status_code}")
        print(exc.response_body)
        raise SystemExit(1) from exc

    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    print(f"Raw: {response.text}")


def confirm_real_api_call(config: Config) -> None:
    if not sys.stdin.isatty():
        raise SystemExit("Interactive terminal confirmation is required for the real API call.")

    print(f"{COLOR_RED}WARNING: this will create a real Datalogics shipment.{COLOR_RESET}")
    print(f"{COLOR_YELLOW}Review the target details before continuing:{COLOR_RESET}")
    print(f"{COLOR_CYAN}Order:{COLOR_RESET} id={config.order_id} number={config.order_number}")
    print(
        f"{COLOR_CYAN}Destination:{COLOR_RESET} "
        f"{config.shipping_city}, {config.shipping_street} {config.shipping_house}"
    )
    print(
        f"{COLOR_CYAN}Recipient:{COLOR_RESET} "
        f"{config.shipping_first_name} {config.shipping_last_name} / {config.shipping_phone}"
    )
    print(
        f"{COLOR_CYAN}Origin:{COLOR_RESET} "
        f"{config.origin_company_name}, {config.origin_city}, "
        f"{config.origin_street} {config.origin_house}"
    )
    answer = input("Type 'yes' to continue: ").strip().lower()
    if answer != "yes":
        raise SystemExit("Cancelled.")


if __name__ == "__main__":
    main()
