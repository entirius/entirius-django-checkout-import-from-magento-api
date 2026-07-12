# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.conf import settings

MAGENTO2_URL_FOR_CHECKOUT_EXPORT = getattr(settings, "MAGENTO2_URL_FOR_CHECKOUT_EXPORT", None)
MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT = getattr(settings, "MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT", None)
