# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from django_checkout.models import Order as CheckoutOrder
from magento2_sdk.client import Client
from magento2_sdk.dto.order import OrderStatus
from magento2_sdk.dto.search import Filter, FilterGroup, SearchCriteria
from magento2_sdk.services import InvoiceService, OrderService

from django_checkout_import_from_magento_api import settings
from django_checkout_import_from_magento_api.models import StatusFromMagento
from django_checkout_import_from_magento_api.repository import order_find_by

from ..bi import DCheckoutImportFromMagentoApiImportOrderStatusEvent

logger = logging.getLogger(__name__)
logger_process = logging.getLogger("process")
# Export używa tego settingsu do pushowania do Magento, więc uznałem, że nie trzeba robić dwóch osobnych.


MAGENTO_URL = settings.MAGENTO2_URL_FOR_CHECKOUT_EXPORT
MAGENTO_TOKEN = settings.MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT

UPDATED_STATUSES_ORDER = [OrderStatus.PROCESSING, OrderStatus.ON_HOLD, OrderStatus.CANCELED, OrderStatus.COMPLETE]


MAGENTO_TO_DJANGO_STATUS = {
    OrderStatus.PROCESSING: "confirmed",  # but only when invoice is created
}


def _has_invoice_in_magento(client: Client, magento_entity_id: str) -> bool:
    """Sprawdza czy dla zamówienia (wg Magento entity_id) istnieje faktura."""
    invoice_service = InvoiceService(client=client)
    criteria = SearchCriteria(
        filter_groups=[FilterGroup(filters=[Filter(field="order_id", value=magento_entity_id, condition_type="eq")])]
    )
    response = invoice_service.get_invoices(search_criteria=criteria)
    total_count = int(response.get("total_count", 0))
    return total_count > 0


def import_order_status_from_magento(
    order_pk: int | None = None, order_id: str | None = None, order_pretty_id: str | None = None
):
    """
    exactly one of: order_pk, order_id or order_pretty_id must be set
    """
    bev = DCheckoutImportFromMagentoApiImportOrderStatusEvent(is_ongoing_event=True)
    report = {
        "order_pk": order_pk,
        "order_id": order_id,
        "order_pretty_id": order_pretty_id,
        "is_order_found": False,
        "is_request_correct": False,
        "is_request_done_with_order": False,
        "is_status_changed": False,
        "magento_fields": {},
    }
    try:
        checkout_order: CheckoutOrder = order_find_by(order_pk, order_id, order_pretty_id)
    except Exception:
        msg = f"Can not find order, can not proceed with Import: order_pk={order_pk} order_id={order_id} order_pretty_id={order_pretty_id}"
        logger.error(msg)
        logger_process.error(
            "Can not find order, can not proceed with Import.",
            extra={"details": {"order_pk": order_pk, "order_id": order_id, "order_pretty_id": order_pretty_id}},
        )
        bev.finish_with_error(finish_tag="Can not find order, can not proceed with Import.", details=report)
        return False

    try:
        order_id = checkout_order.order_id
        order_pretty_id = checkout_order.pretty_id
        report["order_pk"] = checkout_order.pk
        report["order_id"] = order_id
        report["order_pretty_id"] = order_pretty_id
        report["is_order_found"] = True

        order_entity, created = StatusFromMagento.objects.get_or_create(
            checkout_order=checkout_order, defaults={"magento_url": MAGENTO_URL, "success": False, "attempts": 1}
        )
        if not created:
            order_entity.attempts += 1

        client: Client = Client(base_url=MAGENTO_URL, access_token=MAGENTO_TOKEN)
        order_service: OrderService = OrderService(client=client)
        created_at_criteria = SearchCriteria(
            filter_groups=[
                FilterGroup(filters=[Filter(field="increment_id", value=checkout_order.pretty_id, condition_type="eq")])
            ]
        )
        response = order_service.get_orders(search_criteria=created_at_criteria)
        report["is_request_done_with_order"] = True

        # Validate: czy Magento zwróciło error message?
        if response.get("message") is not None:
            order_entity.response = response
            order_entity.internal_message = f"There was a problem with your query {response.get('message')}"
            order_entity.save()
            # Zolv: to nie dziala, nie widac w pliku logo zawartosci extra
            logger_process.error(
                "Magento returned invalid response",
                extra={
                    "details": {
                        "order_id": order_id,
                        "order_pretty_id": order_pretty_id,
                        "message": str(response.get("message")),
                    }
                },
            )
            report["response"] = response
            bev.finish_with_error(finish_tag="Magento returned invalid response", details=report)
            return False

        # Validate: czy Magento zwróciło dokładnie 1 obiekt zamówienia?
        total_count = 0
        if response.get("total_count") is not None:
            total_count = int(response.get("total_count"))
        if total_count != 1:
            order_entity.response = response
            order_entity.internal_message = f"Magento returned {total_count} orders, expected exactly 1"
            order_entity.save()
            logger_process.error(
                "Magento returned invalid response, can not find order data",
                extra={
                    "details": {"order_id": order_id, "order_pretty_id": order_pretty_id, "total_count": total_count}
                },
            )
            report["response"] = response
            bev.finish_with_error(
                finish_tag="Magento returned invalid response, can not find order data", details=report
            )
            return False

        # Validate: czy Magento zwróciło faktycznie dane zamówienia w items[0]?
        order_from_magento = response["items"][0]
        if (
            order_from_magento is None
            or order_from_magento["increment_id"] is None
            or order_from_magento["entity_id"] is None
            or order_from_magento["status"] is None
            or int(order_from_magento["entity_id"]) <= 0
        ):
            order_entity.response = response
            order_entity.internal_message = (
                "Magento returned invalid order data, check: increment_id, entity_id, status"
            )
            order_entity.save()
            logger_process.error(
                "Magento returned invalid order data",
                extra={"details": {"order_id": order_id, "order_pretty_id": order_pretty_id, "response": response}},
            )
            report["response"] = response
            bev.finish_with_error(finish_tag="Magento returned invalid order data", details=report)
            return False

        # Business Logic
        order_entity.response = order_from_magento
        order_entity.entity_id = order_from_magento["entity_id"]
        order_entity.increment_id = order_from_magento["increment_id"]
        status_order = order_from_magento["status"]
        report["is_request_correct"] = True
        report["magento_fields"]["entity_id"] = order_entity.entity_id
        report["magento_fields"]["increment_id"] = order_entity.increment_id
        report["magento_fields"]["status_order"] = status_order

        if status_order in UPDATED_STATUSES_ORDER:
            if status_order == OrderStatus.PROCESSING:
                has_invoice = _has_invoice_in_magento(client, order_entity.entity_id)
                if not has_invoice:
                    logger_process.info(
                        "Skipping, order is processing but no invoice in Magento",
                        extra={"details": {"order_id": order_id, "order_pretty_id": order_pretty_id}},
                    )
                    return True

            report["is_status_changed"] = True
            order_status_prev = checkout_order.order_status
            django_status = MAGENTO_TO_DJANGO_STATUS.get(status_order, status_order)
            report["magento_fields"]["django_status"] = django_status
            is_changed = checkout_order.modify_status(status=django_status)
            if is_changed:
                order_entity.success = True
                order_entity.save()
                logger_process.info(
                    "Order status has been updated.",
                    extra={
                        "details": {
                            "order_id": order_id,
                            "order_pretty_id": order_pretty_id,
                            "order_status_prev": order_status_prev,
                            "order_status": checkout_order.order_status,
                        }
                    },
                )
                report["order_status_prev"] = order_status_prev
                report["order_status"] = checkout_order.order_status
                bev.finish_with_success(finish_tag="Order status has been updated.", details=report)
            else:
                logger_process.info(
                    "Skipped, order status is already up to date",
                    extra={
                        "details": {
                            "order_id": order_id,
                            "order_pretty_id": order_pretty_id,
                            "order_status": checkout_order.order_status,
                        }
                    },
                )
                report["order_status"] = checkout_order.order_status
                bev.finish_with_success(finish_tag="Skipped, order status is already up to date", details=report)
        else:
            order_entity.internal_message = (
                f"Order status: {status_order}. Upload only {', '.join(UPDATED_STATUSES_ORDER)}"
            )
            logger_process.error(
                "Skipping, Magento status order out of list",
                extra={
                    "details": {
                        "order_id": order_id,
                        "order_pretty_id": order_pretty_id,
                        "magento_status_order": status_order,
                    }
                },
            )
            bev.finish_with_success(finish_tag="Skipping, Magento status order out of list", details=report)
        order_entity.save()
        return True

    except Exception as e:
        msg = f"Exception while importing status order from Magento: order_id={order_id} order_pretty_id={order_pretty_id}, message: {e}"
        logger.error(msg)
        logger_process.error(
            "Exception while exporting order to Magento.",
            extra={"details": {"order_id": order_id, "order_pretty_id": order_pretty_id}},
        )
        bev.finish_with_exception(e=e, details=report)
        raise e
