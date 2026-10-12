# entirius-django-checkout-import-from-magento-api

A Django module that imports order statuses from a Magento 2 store into
Entirius, the open-source modular ecommerce platform, over REST. It is the return path of the order export: Magento
processes the order and its status comes back to the checkout.

[![PyPI](https://img.shields.io/pypi/v/entirius-django-checkout-import-from-magento-api.svg)](https://pypi.org/project/entirius-django-checkout-import-from-magento-api/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-django-checkout-import-from-magento-api.svg)](https://pypi.org/project/entirius-django-checkout-import-from-magento-api/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-django-checkout-import-from-magento-api/blob/develop/LICENSE)

## What it does

- Reads the Magento status of one order, or of every order created in the last days.
- Updates the checkout order when Magento reports it on hold, canceled or complete.
- Confirms a processing order once Magento holds an invoice for it.
- Keeps the Magento response, a success flag and the attempt count per order.

## Installation

```shell
uv add entirius-django-checkout-import-from-magento-api
pip install entirius-django-checkout-import-from-magento-api
```

```python
INSTALLED_APPS = [
    ...
    "django_checkout",
    "django_checkout_import_from_magento_api",
]
```

`django_checkout` brings its own app requirements. Required settings: `MAGENTO2_URL_FOR_CHECKOUT_EXPORT` and
`MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT`.
The module also reads `BI_ENVIRONMENT` and `BI_BUSINESS_UNIT` (BI events) at import time, without a default.

Both settings are shared with `entirius-django-checkout-export-to-magento-api`: one Magento endpoint serves the
export and the status import. Reference: https://github.com/entirius/entirius-django-checkout-import-from-magento-api/blob/develop/AGENTS.md (section Settings).

## Quick start

```python
# settings.py
MAGENTO2_URL_FOR_CHECKOUT_EXPORT = "https://magento.example.com/rest/"
MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT = "<api-token>"

# a shell or a scheduled job
from django.core.management import call_command

call_command("import-orders-status-from-magento", days=7)
```

`days` is how far back orders are looked up by creation date (default 1). One order:
`import-order-status-from-magento <order_id>`.

## Requirements

- Python 3.11 or newer, Django 5.0 or newer.
- PostgreSQL.
- A Magento 2 store with a REST API integration token.
- Entirius packages pulled in: `entirius-django-checkout` (orders and status updates), `entirius-py-magento2-sdk`
  (Magento 2 REST client), `entirius-py-bievents` (BI events).

## Documentation

- Module docs (management commands, process logging): https://github.com/entirius/entirius-django-checkout-import-from-magento-api/tree/develop/docs
- Entirius documentation: https://docs.entirius.com/
- Releases: https://github.com/entirius/entirius-django-checkout-import-from-magento-api/releases

## Part of Entirius

This module runs inside the Entirius backend service (Volkanos) and reads order statuses back from an existing
Magento 2 store.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Checkout module: https://github.com/entirius/entirius-django-checkout
- Magento 2 SDK it uses: https://github.com/entirius/entirius-py-magento2-sdk
- Sibling bridges: https://github.com/entirius/entirius-django-checkout-export-to-magento-api,
  https://github.com/entirius/entirius-django-pim-export-to-magento-api,
  https://github.com/entirius/entirius-django-accounts-export-to-magento-api

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django, needs PostgreSQL via DATABASE_URL)
```

Development and agent instructions: https://github.com/entirius/entirius-django-checkout-import-from-magento-api/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-django-checkout-import-from-magento-api/blob/develop/LICENSE.
