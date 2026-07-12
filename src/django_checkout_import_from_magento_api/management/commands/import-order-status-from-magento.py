# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from bievents import bi_django_command_decorator
from django.core.management.base import BaseCommand

from django_checkout_import_from_magento_api.tasks import import_order_status_from_magento


class Command(BaseCommand):
    help = "Import Order Status from Magento2"

    def add_arguments(self, parser):
        parser.add_argument("order_id", type=str, help="use order_id (10 chars) or order_pretty_id (36 chars)")

    @bi_django_command_decorator
    def handle(self, *args, **options):
        order_id_raw = options["order_id"]
        order_id = None
        order_pretty_id = None

        if len(order_id_raw) == 10:
            order_pretty_id = order_id_raw
        elif len(order_id_raw) == 36:
            order_id = order_id_raw
        else:
            raise ValueError("Order id is invalid, use order_id (10 chars) or order_pretty_id (36 chars)")
        rv = import_order_status_from_magento(order_id=order_id, order_pretty_id=order_pretty_id)
        if rv:
            self.stdout.write(self.style.SUCCESS("done"))
        else:
            self.stdout.write(self.style.ERROR("error"))
