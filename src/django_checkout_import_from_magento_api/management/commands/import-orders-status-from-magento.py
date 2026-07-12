# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import timedelta

from bievents import bi_django_command_decorator
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_checkout.models import Order

from django_checkout_import_from_magento_api.tasks import import_order_status_from_magento

DAYS = 1


class Command(BaseCommand):
    help = (
        "| Import Orders Status from Magento2. Conditions: "
        " | Default number of days from which orders can be status taken: " + str(DAYS) + ""
    )

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int)

    @bi_django_command_decorator
    def handle(self, *args, **options):
        days = DAYS
        if options["days"] is not None:
            days = options["days"]
        orders: list[Order] = Order.objects.filter(created__gte=timezone.now() - timedelta(days=days))
        errors = 0
        exceptions = 0
        for order in orders:
            try:
                self.stdout.write("Process pulling status for order: " + order.pretty_id)
                rv = import_order_status_from_magento(order_pk=order.pk)
                if not rv:
                    errors += 1
            except Exception:
                exceptions += 1
                print(f"Exception while processing order {order.pretty_id}")
        if len(orders) == 0:
            print("No orders to process found")
        if errors > 0:
            print(f"Errors while processing orders: {errors}")
        if exceptions > 0:
            print(f"Exceptions while processing orders: {errors}")
        self.stdout.write(self.style.SUCCESS("done"))
