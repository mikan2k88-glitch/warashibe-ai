"""PG-029 Purchase Receipt / Reconciliation contract tests."""

from research_lab.purchase_receipt_reconciliation import reconcile_purchase_receipt


def _execution():
    return {
        "status":"single_purchase_executed",
        "idempotency_key":"idem-029",
        "confirmation_key":"fb-029",
        "provider":"yahoo_shopping",
        "item_key":"item-029",
        "quantity":1,
        "order_reference":"order-029",
        "charged_amount_jpy":2950,
        "order_created":True,
        "payment_created":True,
        "human_final_buy_recorded":True,
        "executed_at":"2026-10-03T04:00:00+00:00",
    }


def main():
    receipt=reconcile_purchase_receipt(
        _execution(),
        receipt_key="receipt-029",
        provider_order_reference="order-029",
        actual_item_price_jpy=2800,
        actual_shipping_jpy=150,
        actual_tax_jpy=0,
        actual_discount_jpy=0,
        actual_total_charged_jpy=2950,
        currency="JPY",
        payment_status="captured",
        order_status="confirmed",
        reconciled_at="2026-10-03T04:05:00+00:00",
    )
    assert receipt["status"]=="purchase_receipt_reconciled"
    assert receipt["reconciliation_passed"] is True
    assert receipt["charge_variance_jpy"]==0
    assert receipt["actual_total_charged_jpy"]==2950
    assert receipt["capital_committed_jpy"]==2950
    assert receipt["capital_state"]=="awaiting_receipt_or_delivery"

    bad=reconcile_purchase_receipt(
        _execution(),
        receipt_key="receipt-029-bad",
        provider_order_reference="order-029",
        actual_item_price_jpy=2800,
        actual_shipping_jpy=150,
        actual_tax_jpy=0,
        actual_discount_jpy=0,
        actual_total_charged_jpy=3050,
        currency="JPY",
        payment_status="captured",
        order_status="confirmed",
        reconciled_at="2026-10-03T04:05:00+00:00",
    )
    assert bad["status"]=="purchase_receipt_mismatch"
    assert bad["reconciliation_passed"] is False
    assert bad["charge_variance_jpy"]==100
    assert bad["requires_human_review"] is True

    print("PG-029 Purchase Receipt / Reconciliation tests passed")


if __name__=="__main__":
    main()
