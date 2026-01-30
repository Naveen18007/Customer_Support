from app.utils.supabase_client import supabase

def get_customer_orders(customer_id: str):
    """
    Get customer billing information - supports both orders and subscriptions.
    Returns unified format with order_id/product_name/amount for orders,
    and plan/price for subscriptions.
    """
    response = (
        supabase
        .table("billing")
        .select("order_id, product_name, amount, plan, price, status, billing_type, next_billing_date, payment_method")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .execute()
    )

    if not response.data:
        return []

    # Normalize the data format for the billing agent
    normalized_data = []
    for item in response.data:
        if item.get("billing_type") == "order" or item.get("order_id"):
            # Order-based billing
            normalized_data.append({
                "order_id": item.get("order_id", f"O{item.get('id', '')}"),
                "product_name": item.get("product_name", "Unknown Product"),
                "amount": float(item.get("amount", 0)),
                "status": item.get("status", "unknown").upper(),
                "type": "order"
            })
        else:
            # Subscription-based billing
            normalized_data.append({
                "order_id": f"SUB-{item.get('id', '')}",
                "product_name": f"{item.get('plan', 'Unknown Plan')} Subscription",
                "amount": float(item.get("price", 0)),
                "status": item.get("status", "unknown").upper(),
                "type": "subscription",
                "next_billing_date": item.get("next_billing_date"),
                "payment_method": item.get("payment_method")
            })
    
    return normalized_data
