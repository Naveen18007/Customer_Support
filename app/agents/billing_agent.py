from app.services.billing_service import get_customer_orders
from app.services.email_service import send_email
from app.utils.billing_formatter import format_billing_email
from app.services.user_service import get_user_email  # assumes you have this


def generate_billing_response(customer_id: str, message: str) -> str:
    orders = get_customer_orders(customer_id)

    if not orders:
        return "🧾 No billing records found for your account."

    # 📧 Send Email
    user_email = get_user_email(customer_id)
    email_body = format_billing_email(orders)

    send_email(
        to_email=user_email,
        subject="Your Billing Details",
        body=email_body
    )

    # 💬 Chat Response
    response_lines = ["🧾 **Your Billing Details (also sent to your email):**\n"]

    for order in orders:
        response_lines.append(
            f"• Order ID: {order['order_id']}\n"
            f"  Product: {order['product_name']}\n"
            f"  Amount: ${order['amount']:.2f}\n"
            f"  Status: {order['status']}\n"
        )
        
        # Add subscription-specific info if applicable
        if order.get('type') == 'subscription' and order.get('next_billing_date'):
            response_lines.append(f"  Next Billing: {order['next_billing_date']}\n")
        if order.get('payment_method'):
            response_lines.append(f"  Payment Method: {order['payment_method']}\n")
        
        response_lines.append("")  # Empty line between items

    return "\n".join(response_lines)
