# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin

from .models import StatusFromMagento


@admin.register(StatusFromMagento)
class StatusFromMagento(admin.ModelAdmin):
    model = StatusFromMagento

    list_display = ["checkout_order", "magento_url", "success", "attempts", "entity_id", "increment_id"]
    list_filter = ["success", "magento_url"]
    search_fields = ["checkout_order__pk", "checkout_order__order_id", "increment_id"]

    readonly_fields = [
        "checkout_order",
        "magento_url",
        "success",
        "attempts",
        "response",
        "entity_id",
        "increment_id",
        "internal_message",
    ]
