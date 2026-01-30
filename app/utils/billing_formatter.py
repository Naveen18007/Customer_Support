def format_billing_email(orders: list) -> str:
    lines = [
        "Hello,\n",
        "Here are your billing details:\n"
    ]

    for order in orders:
        lines.append(
            f"Order ID: {order['order_id']}\n"
            f"Product: {order['product_name']}\n"
            f"Amount: ${order['amount']}\n"
            f"Status: {order['status']}\n"
            "-----------------------------\n"
        )

    lines.append("\nThank you for choosing us.")
    return "".join(lines)
