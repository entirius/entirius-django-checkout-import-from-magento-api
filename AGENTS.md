# AGENTS.md

Import of order statuses from the Magento 2 API back into Volkanos checkout — distribution
`entirius-django-checkout-import-from-magento-api`, Django app `django_checkout_import_from_magento_api`.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest + pytest-django) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the package / Django app_label / DB table prefix `django_checkout_import_from_magento_api` — it is a schema contract.
- Migrations are part of the public contract — never edit an already released migration.
- Default: do not commit — git is the user's call.

## Architecture

```
src/django_checkout_import_from_magento_api/
├── apps.py                 # AppConfig (is_volkanos=True)
├── settings.py             # host-overridable settings (Magento URL/token via getattr)
├── models.py               # StatusFromMagento (OneToOne → django_checkout.Order, attempts counter)
├── repository.py           # order lookups (by pk / order_id / pretty_id)
├── dto.py                  # OrderIdType helper
├── bi.py                   # BI events (bievents)
├── admin.py                # StatusFromMagento admin
├── tasks/                  # import_order_status_from_magento (called by commands, synchronous)
└── management/commands/    # import-order-status-from-magento, import-orders-status-from-magento
```

`StatusFromMagento` keeps one row per checkout order: the Magento response, success flag and the
number of import attempts. Orders are updated only when the Magento status is ON_HOLD, CANCELED
or COMPLETE.

## Dependencies

| Module | Purpose |
|---|---|
| `django_checkout` | Order (OneToOne FK + status updates) |
| `magento2_sdk` | Magento 2 REST client (orders, invoices) |
| `bievents` | BI command decorators + events |

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `MAGENTO2_URL_FOR_CHECKOUT_EXPORT` | `None` | Magento REST base URL (shared with the export module) |
| `MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT` | `None` | Magento API token (shared with the export module) |

## Testing

```bash
# Postgres required; tests/settings.py reads DATABASE_URL
# (default postgresql://postgres:postgres@localhost:5432/test).
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test make test
```

Test suite is an import smoke test (`tests/test_smoke.py`) — real importer tests are an open TODO.

## References

- `docs/commands/` — management command reference (parameters, examples).
