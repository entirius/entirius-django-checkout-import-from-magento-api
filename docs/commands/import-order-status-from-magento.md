# Command

## Import order status from magento

```bash
manage.py import-checkout-order-from-magento --order_primary_key=1 --order_id="123awd2a2312d1" --order_pretty_id="10000004"
```

Paramteters (only one at a time of them is required):

| Name              | Type | Optional | Default |
|-------------------|------|----------|---------|
| order_primary_key | int  | +        | -       |
| order_id          | str  | +        | -       |
| order_pretty_id   | str  | +        | -       |


## Import order statuses from magento

```bash
manage.py import-checkout-orders-from-magento --days=1
```

Paramteters:

| Name | Type | Optional | Default |
|------|------|----------|---------|
| days | int  | +        | 1       |

Conditions:
- Only orders with created date in range of last days of parameter
- Only updated orders with status: ON_HOLD, CANCELED, COMPLETE