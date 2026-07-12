# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Smoke test: every public submodule imports cleanly under a configured Django."""

import importlib

import pytest

MODULES = [
    "django_checkout_import_from_magento_api.apps",
    "django_checkout_import_from_magento_api.settings",
    "django_checkout_import_from_magento_api.models",
    "django_checkout_import_from_magento_api.admin",
    "django_checkout_import_from_magento_api.bi",
    "django_checkout_import_from_magento_api.dto",
    "django_checkout_import_from_magento_api.repository",
    "django_checkout_import_from_magento_api.tasks",
    "django_checkout_import_from_magento_api.tasks.import_order_status_from_magento",
    "django_checkout_import_from_magento_api.management.commands.import-order-status-from-magento",
    "django_checkout_import_from_magento_api.management.commands.import-orders-status-from-magento",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    importlib.import_module(module)
