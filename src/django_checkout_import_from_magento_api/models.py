# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django_checkout.models.order import Order as CheckoutOrder


class StatusFromMagento(models.Model):
    # checkout_order: "CheckoutOrder" = models.ForeignKey(
    #     "django_checkout.Order",
    #     related_name="status_order_in_magento",
    #     null=False,
    #     unique=True,
    #     on_delete=models.CASCADE,
    # )
    checkout_order: "CheckoutOrder" = models.OneToOneField(
        "django_checkout.Order", related_name="status_order_in_magento", null=False, on_delete=models.CASCADE
    )
    magento_url = models.CharField(max_length=255)
    success = models.BooleanField(default=False, help_text="Magento status in: ON_HOLD, CANCELED, COMPLETE]")
    response = models.JSONField(null=True)
    entity_id = models.CharField(max_length=100, null=True, blank=True)
    increment_id = models.CharField(max_length=100, null=True, blank=True)
    internal_message = models.CharField(max_length=255, null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0, help_text="Number of import attempts made")
    objects = models.Manager()

    class Meta:
        verbose_name = "Status from Magento"
        verbose_name_plural = "Statuses from Magento"
