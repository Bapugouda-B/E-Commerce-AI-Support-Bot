from datetime import datetime, timedelta

MOCK_ORDERS = {
    "ORD123": {
        "status": "Processing",
        "created_at": datetime.now() - timedelta(days=2),
        "expected_delivery": datetime.now() + timedelta(days=4),
        "total_amount": 1499.0,
    },
    "ORD456": {
        "status": "Shipped",
        "created_at": datetime.now() - timedelta(days=3),
        "expected_delivery": datetime.now() + timedelta(days=2),
        "total_amount": 899.0,
    },
    "ORD789": {
        "status": "Delivered",
        "created_at": datetime.now() - timedelta(days=7),
        "expected_delivery": datetime.now() - timedelta(days=2),
        "total_amount": 2499.0,
    },
}


MOCK_RETURNS = []  # store created return requests in memory


def get_order_status(order_id: str) -> str:
    """Mock: return human‑readable status for an order id."""
    oid = order_id.upper().rstrip("?.")  # strip trailing ? or .
    order = MOCK_ORDERS.get(oid)
    if not order:
        return (
            f"I could not find any order with ID {oid}. "
            "Please double‑check the ID on your 'My Orders' page before trying again."
        )

    status = order["status"]
    eta = order["expected_delivery"].strftime("%d %b %Y")
    created = order["created_at"].strftime("%d %b %Y")

    if status == "Processing":
        detail = (
            "your order has been received and is being prepared for shipment at our warehouse."
        )
    elif status == "Shipped":
        detail = (
            "your order has left the warehouse and is with the courier partner. "
            "You will find a tracking link on the 'My Orders' page for live updates."
        )
    elif status == "Delivered":
        detail = (
            "your order has already been delivered. If you did not receive it, "
            "please contact customer support as soon as possible."
        )
    else:
        detail = "your order is in the current status."

    return (
        f"Order {oid} is currently **{status}**. "
        f"It was placed on {created}, and the expected delivery date is {eta}. "
        f"In simple terms, {detail}"
    )


def create_return_request(order_id: str, reason: str) -> str:
    """Mock: create a return request and store it in memory."""
    order = MOCK_ORDERS.get(order_id.upper())
    if not order:
        return (
            f"I could not find an order with ID {order_id}. "
            "Please verify the ID in your 'My Orders' page before requesting a return."
        )

    # Very simple rule: allow return only if delivered within last 10 days
    days_since_delivery = (datetime.now() - order["expected_delivery"]).days
    if order["status"] != "Delivered" or days_since_delivery > 10:
        return (
            "This order is not currently eligible for a return through the chatbot. "
            "Returns are usually allowed only for recently delivered orders within "
            "the return window shown on the product page."
        )

    request_id = f"RET-{order_id.upper()}"
    MOCK_RETURNS.append(
        {
            "request_id": request_id,
            "order_id": order_id.upper(),
            "reason": reason,
            "created_at": datetime.now(),
        }
    )

    return (
        f"A return request **{request_id}** has been created for order {order_id} "
        f"with reason: '{reason}'. Our team will review it and share pickup details "
        "by email or SMS within 1–2 business days."
    )


def get_refund_policy() -> str:
    """Mock: return a friendly explanation of refund policy."""
    return (
        "Refunds are usually processed after the returned item is picked up and "
        "passes a quality check. For most orders, this takes 5–7 business days "
        "from the date of pickup. Refunds are sent back to the original payment "
        "method whenever possible. For Cash on Delivery orders, the refund is "
        "typically issued to your bank account, UPI ID, or as store credit, "
        "depending on your preference during the return process."
    )

def payment_failed_help() -> str:
    return (
        "If your payment failed but money was deducted, the amount is usually "
        "reversed automatically by your bank or payment provider within 5–7 "
        "business days. If the amount is not credited back after this period, "
        "please contact customer support with your transaction reference number."
    )


def double_charge_help() -> str:
    return (
        "If you were charged twice for the same order, one of the charges is "
        "usually reversed automatically within 5–7 business days. "
        "If both charges remain after that, please contact customer support "
        "with both transaction IDs for quick resolution."
    )
