# datalogic-sdk

Independent/community Python SDK for the Datalogics shipping API.

This is not an official Datalogics SDK. It is an independent/community project.

## Documentation

- [Usage guide](docs/usage.md): how to use this Python SDK.
- [SDK API reference](docs/api.md): Python classes, methods, return values, and exceptions.
- [OpenAPI contract](docs/openapi.yaml): raw Datalogics HTTP API contract for
  `POST /rest/w_create_shipping`.
- [Contributing guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Security policy](SECURITY.md)

The OpenAPI file documents the vendor HTTP endpoint, not the Python SDK itself.
It is included as a reference for API tooling, contract review, mock servers, or
future code generation. The SDK does not load it at runtime.

## Installation

From this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

This project currently has no third-party runtime dependencies. The
`requirements.txt` file is intentionally empty except for a comment.

If you only want to run from a checkout without installing:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Development

Install the SDK and dev tooling inside a virtual environment:

```bash
make install
```

Available commands:

```bash
make format
make lint
make typecheck
make test
make check
make integration-test
make package
make release
```

`make package` builds the source distribution and wheel into `dist/`.
`make release` increments the latest `vX.Y.Z` tag by one patch version, updates
`pyproject.toml`, runs verification, commits the version bump, creates an
annotated tag, pushes the branch, and pushes the tag.
`make check` runs lint, typecheck, and tests.
`make integration-test` runs the real API integration script.

## CI/CD

GitHub Actions workflows live in `.github/workflows/`.

- `ci.yml` runs on pull requests to `main` and manual dispatch. It installs the
  package with dev tooling, then runs lint, typecheck, and tests across Python
  3.9 through 3.13, and builds the package once on Python 3.13.
- `release.yml` runs only on tags matching `v*`. It runs the same checks,
  builds `dist/`, uploads the distribution files as a workflow artifact,
  creates a GitHub Release, and publishes to PyPI through Trusted Publishing.
- PyPI publishing does not use a stored API token. Configure a pending trusted
  publisher in PyPI with these values:
  - PyPI project name: `datalogic-sdk`
  - Owner: `yair-ros`
  - Repository name: `datalogic-sdk`
  - Workflow name: `release.yml`
  - Environment name: `pypi`

To create a GitHub Release and trigger PyPI publishing:

```bash
make release
```

If your virtual environment is not activated, pass the interpreter explicitly:

```bash
make release PYTHON=.venv/bin/python
```

## Usage

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
            phone="0501234567",
            # Use n_code only when the customer chose a pickup location.
            n_code="PICKUP_LOCATION_ID",
        ),
        comment="Leave at reception",
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

## Validation

The SDK validates the request before sending it:

- `token` is required.
- `order.id` and `order.number` are required.
- Required shipping fields: `street`, `city`, `first_name`, `last_name`, `house`, `phone`.
- Optional shipping fields: `postcode`, `apartment`, `n_code`.
- `origin.contract` must be exactly 4 characters.
- Required origin fields: `company_name`, `city`, `street`, `house`, `phone`, `email`.

## Error Handling

```python
from datalogic_sdk import (
    DatalogicAPIError,
    DatalogicClient,
    DatalogicValidationError,
    Order,
    Origin,
    ShippingDetails,
)

client = DatalogicClient("YOUR_AUTHENTICATION_TOKEN")
order = Order(
    id=123,
    number="ORD-123",
    shipping=ShippingDetails(
        street="Herzl",
        city="Tel Aviv",
        first_name="Dana",
        last_name="Cohen",
        house="10",
        phone="0501234567",
    ),
)
origin = Origin(
    contract="1234",
    company_name="Acme Ltd",
    city="Jerusalem",
    street="Jaffa",
    house="1",
    phone="021234567",
    email="ops@example.com",
)

try:
    response = client.create_shipping(order=order, origin=origin)
except DatalogicValidationError as exc:
    print(f"Invalid request: {exc}")
except DatalogicAPIError as exc:
    print(f"API error {exc.status_code}: {exc.response_body}")
```

## Endpoint

By default the client calls:

```text
https://connect.datalogics.co.il/rest/w_create_shipping
```

You can override the base URL for testing:

```python
from datalogic_sdk import DatalogicClient

client = DatalogicClient("token", base_url="https://example.test")
```

## Real API Test

The repository includes a local integration-test script:

```bash
PYTHONPATH=src python scripts/integration_test.py
```

The test reads local secrets and addresses from:

```text
scripts/integration_test.env
```

That file is gitignored. The repository only includes:

```text
scripts/integration_test.env.example
```

To use it:

1. Copy `scripts/integration_test.env.example` to `scripts/integration_test.env`.
2. Fill your real token and address data in `scripts/integration_test.env`.
3. Set `DATALOGIC_CONFIRM_REAL_API_CALL=yes` in that file.
4. Run `make integration-test` or `PYTHONPATH=src python scripts/integration_test.py`.
5. Read the warning in the terminal and type `yes` to approve the real shipment creation.

This can create a real shipment. Use a sandbox/test token if Datalogics provides
one, and do not commit real tokens, customer phones, or real addresses.

The script fails fast if:

- `scripts/integration_test.env` does not exist
- `DATALOGIC_CONFIRM_REAL_API_CALL` is not `yes`
- a required value is missing
- a required value is still one of the example placeholders such as `YOUR_TOKEN`
- the terminal confirmation is not explicitly approved

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE).
