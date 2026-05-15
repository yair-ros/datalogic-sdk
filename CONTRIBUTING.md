# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

## Before Opening a Pull Request

Run:

```bash
make check
```

If you changed packaging or release behavior, also run:

```bash
make package
```

## Integration Testing

The real API integration test uses local-only data from:

```text
scripts/integration_test.env
```

That file is gitignored. Do not commit real tokens, phone numbers, addresses,
or shipping data.

To prepare it:

```bash
cp scripts/integration_test.env.example scripts/integration_test.env
```

Then fill real values locally and run:

```bash
make integration-test
```

## Style

- Keep changes focused.
- Follow the existing project structure.
- Prefer standard library solutions unless a dependency is justified.
- Update documentation when behavior changes.
- Add or update tests when the change affects behavior.

## Releases

Releases are created with:

```bash
make release
```

That command bumps the patch version, verifies the project, commits the version
change, creates a tag, and pushes both branch and tag.
