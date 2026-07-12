# entirius-django-checkout-import-from-magento-api

Imports order statuses from a Magento 2 instance back into `django_checkout` via the Magento REST API.
Only orders whose Magento status is ON_HOLD, CANCELED or COMPLETE are updated.
Part of the Volkanos e-commerce module family.

## Installation

```shell
pip install entirius-django-checkout-import-from-magento-api
```

## Configuration

```python
MAGENTO2_URL_FOR_CHECKOUT_EXPORT = "https://your-magento-host/rest/"
MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT = "<api-token>"
```

## Development

```shell
make install   # uv sync (incl. extras)
make test      # run tests
make check     # ruff lint + format-check
```

## Process Logging

Commands can save logs into process.log. Add the following to the host service `settings.py`
(assuming a `process` handler with a JSON formatter is already configured):

```python
LOGGING["loggers"]["django_checkout_import_from_magento_api"] = {
    "handlers": ["process"],
    "level": "DEBUG",
    "propagate": False,
}
```

## Commands

See `docs/commands/` for the management command reference.

## License

MPL-2.0
