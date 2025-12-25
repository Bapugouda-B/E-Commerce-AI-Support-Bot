from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

MOCK_ORDERS = {
    "ORD123": {
        "status": "Processing",
        "created_at": datetime.now() - timedelta(days=2),
        "expected_delivery": datetime.now() + timedelta(days=4),
        "total_amount": 1499.0,
        "items": ["Wireless Headphones", "Phone Case"],
        "customer_name": "Raj Kumar",
    },
    "ORD456": {
        "status": "Shipped",
        "created_at": datetime.now() - timedelta(days=3),
        "expected_delivery": datetime.now() + timedelta(days=2),
        "total_amount": 899.0,
        "items": ["Running Shoes Size 10"],
        "customer_name": "Priya Singh",
    },
    "ORD789": {
        "status": "Delivered",
        "created_at": datetime.now() - timedelta(days=7),
        "expected_delivery": datetime.now() - timedelta(days=2),
        "total_amount": 2499.0,
        "items": ["Smart Watch", "Watch Strap"],
        "customer_name": "Amit Patel",
    },
    "ORD999": {
        "status": "Pending",
        "created_at": datetime.now() - timedelta(hours=2),
        "expected_delivery": datetime.now() + timedelta(days=5),
        "total_amount": 3499.0,
        "items": ["Laptop Stand", "USB-C Cable"],
        "customer_name": "Sara Ahmed",
    },
}

MOCK_PRODUCTS = {
    "wireless headphones": {
        "price": 2499,
        "stock": 45,
        "category": "Electronics",
        "rating": 4.5,
        "reviews": 230,
    },
    "running shoes": {
        "price": 3999,
        "stock": 12,
        "category": "Footwear",
        "rating": 4.7,
        "reviews": 150,
    },
    "smart watch": {
        "price": 5999,
        "stock": 8,
        "category": "Electronics",
        "rating": 4.3,
        "reviews": 89,
    },
    "phone case": {
        "price": 499,
        "stock": 156,
        "category": "Accessories",
        "rating": 4.2,
        "reviews": 420,
    },
}

MOCK_COUPONS = {
    "SAVE20": {"discount": 0.20, "min_amount": 1000, "valid": True},
    "FLAT100": {"discount": 100, "min_amount": 500, "valid": True},
    "NEWUSER": {"discount": 0.50, "min_amount": 2000, "valid": True},
    "EXPIRED2023": {"discount": 0.30, "min_amount": 500, "valid": False},
}

MOCK_RETURNS = []
COMPLAINT_LOG = []


def get_order_status(order_id: str) -> str:
    """Get detailed order status with tracking info"""

    # Clean the order ID: remove extra spaces, punctuation, convert to uppercase
    oid = order_id.upper().strip().rstrip("?.,!;:").replace(" ", "")

    # Remove "ORDER" if it appears separately
    oid = oid.replace("ORDER ", "").replace("ORDER", "")

    order = MOCK_ORDERS.get(oid)

    if not order:
        return (
            f"❌ Order not found: **{oid}**\n\n"
            "Couldn't locate this order ID in our system.\n\n"
            "**What you can do:**\n"
            "✓ Double-check your Order ID\n"
            "✓ Check your email confirmation\n"
            "✓ Visit 'My Orders' on our website\n"
            "✓ Contact support if still stuck\n\n"
            "📧 support@ecommerce.com | 📞 1-800-123-456"
        )

    status = order["status"]
    eta = order["expected_delivery"].strftime("%d %b %Y")
    created = order["created_at"].strftime("%d %b %Y")
    items = ", ".join(order.get("items", ["Item"]))

    status_emojis = {
        "Pending": "⏳",
        "Processing": "⚙️",
        "Shipped": "🚚",
        "Delivered": "✅",
        "Cancelled": "❌",
    }

    emoji = status_emojis.get(status, "📦")

    if status == "Processing":
        detail = (
            "Your order is being **carefully prepared** at our warehouse. "
            "We're picking items, quality checking, and packing for you!"
        )
        next_action = "Next update: Shipping in 1-2 days"
    elif status == "Shipped":
        detail = (
            "Your order is **on its way!** 🎉\n"
            "It's with our courier partner and you should receive it soon."
        )
        next_action = f"Expected: {eta}"
        tracking_info = f"📍 **Live tracking:** Check 'My Orders' > Track Package"
    elif status == "Delivered":
        detail = "Your order has been **successfully delivered!** 🎊"
        next_action = "If you have any issues, start a return within 10 days"
        tracking_info = ""
    elif status == "Pending":
        detail = (
            "Your order is **confirmed** and waiting to be processed. "
            "We'll start preparing it shortly."
        )
        next_action = "Processing starts in 1-2 hours"
        tracking_info = ""
    else:
        detail = f"Your order status is: {status}"
        next_action = "Contact support for more details"
        tracking_info = ""

    response = (
        f"{emoji} **Order {oid} Status**\n\n"
        f"**Status:** {status}\n"
        f"**Items:** {items}\n"
        f"**Amount:** ₹{order['total_amount']:,.0f}\n"
        f"**Order Date:** {created}\n"
        f"**Est. Delivery:** {eta}\n\n"
        f"{detail}\n\n"
        f"**What's next?**\n{next_action}"
    )

    if status == "Shipped":
        response += f"\n{tracking_info}"

    return response


def create_return_request(order_id: str, reason: str) -> str:
    """Create return request with validation"""
    oid = order_id.upper().strip()
    order = MOCK_ORDERS.get(oid)

    if not order:
        return (
            f"❌ Can't find order **{oid}**\n\n"
            "Please verify the Order ID and try again."
        )

    # Check eligibility
    days_since_delivery = (datetime.now() - order["expected_delivery"]).days

    if order["status"] != "Delivered":
        return (
            f"⏸️ Can't return yet\n\n"
            f"**Current status:** {order['status']}\n"
            "Returns are only available for **Delivered** orders.\n\n"
            "Once delivered, you'll have **10 days** to start a return. "
            "Come back after delivery!"
        )

    if days_since_delivery > 10:
        return (
            f"⏰ Return window closed\n\n"
            f"This order was delivered **{days_since_delivery} days ago**.\n"
            "The standard return window is **10 days**.\n\n"
            "**Options:**\n"
            "💬 Contact support to request exception\n"
            "📧 support@ecommerce.com\n"
            "📞 1-800-123-456"
        )

    if days_since_delivery < 0:
        return (
            f"⏰ Order not yet delivered\n\n"
            f"Expected delivery: {order['expected_delivery'].strftime('%d %b %Y')}\n"
            "You can start a return once it's delivered."
        )

    # Create return
    request_id = f"RET-{oid}-{random.randint(1000, 9999)}"
    return_obj = {
        "request_id": request_id,
        "order_id": oid,
        "reason": reason,
        "created_at": datetime.now(),
        "status": "pending_approval",
    }
    MOCK_RETURNS.append(return_obj)

    logger.info(f"Return created: {request_id} for order {oid}")

    return (
        f"✅ Return request created!\n\n"
        f"**Request ID:** {request_id}\n"
        f"**Order ID:** {oid}\n"
        f"**Reason:** {reason[:100]}\n\n"
        "**What happens next?**\n"
        "1️⃣ We review your request (usually within 2 hours)\n"
        "2️⃣ You'll get a **pickup instruction** via SMS/Email\n"
        "3️⃣ Courier collects the package from you\n"
        "4️⃣ We inspect & process refund (5-7 business days)\n\n"
        "💡 **Keep your Request ID handy for tracking!**"
    )


def get_refund_policy() -> str:
    """Detailed refund policy with timeline"""
    return (
        "💰 **Our Refund Policy**\n\n"
        "**Return Eligibility**\n"
        "✅ Items unused, unwashed, in original packaging\n"
        "✅ All original tags attached\n"
        "✅ Within 10 days of delivery\n\n"
        "**Refund Timeline**\n"
        "1️⃣ **Approval:** 2-4 hours after request\n"
        "2️⃣ **Pickup:** 1-2 days (free for defective items)\n"
        "3️⃣ **Inspection:** 1-2 days at warehouse\n"
        "4️⃣ **Refund Processing:** 5-7 business days\n"
        "5️⃣ **Bank Credit:** 2-5 days (varies by bank)\n\n"
        "**Where does refund go?**\n"
        "💳 **Card/UPI/Wallet:** Credited to original payment method\n"
        "💵 **Cash on Delivery:** Bank transfer or store credit\n\n"
        "**Non-Returnable Items**\n"
        "❌ Innerwear, swimwear (hygiene)\n"
        "❌ Personal care products (opened)\n"
        "❌ Customized/personalized items\n"
        "❌ Clearance/Final sale items\n\n"
        "**Questions?**\n"
        "📧 Email: support@ecommerce.com\n"
        "📞 Phone: 1-800-123-456"
    )


def payment_failed_help() -> str:
    """Help for failed payment scenarios"""
    return (
        "❌ **Payment Failed?**\n\n"
        "**First, check:**\n"
        "1️⃣ Internet connection is stable\n"
        "2️⃣ Card/UPI details are correct\n"
        "3️⃣ Sufficient balance/credit limit\n"
        "4️⃣ No bank/card restrictions\n\n"
        "**Money Deducted but No Order Created?**\n"
        "Don't worry! This happens sometimes.\n"
        "✓ Your bank will **auto-reverse** within 5-7 business days\n"
        "✓ No manual action needed\n\n"
        "**Still not reversed after 7 days?**\n"
        "📧 Email with transaction ID: support@ecommerce.com\n"
        "📞 Call us: 1-800-123-456\n\n"
        "**Want to try again?**\n"
        "Try a different:\n"
        "💳 Card\n"
        "💰 UPI account\n"
        "📱 Payment method\n\n"
        "We support: Cards, UPI, Net Banking, Wallets, COD"
    )


def double_charge_help() -> str:
    """Help for double charge scenarios"""
    return (
        "🚨 **Charged Twice?**\n\n"
        "**Here's what likely happened:**\n"
        "When you clicked 'Pay' multiple times (happens to many!), "
        "it might have created 2 transactions.\n\n"
        "**Don't panic! We handle this:**\n"
        "✓ One charge will reverse automatically\n"
        "✓ Usually within 5-7 business days\n"
        "✓ No manual action needed from you\n\n"
        "**Both charges still there after 7 days?**\n"
        "Contact us immediately with:\n"
        "📝 Both Transaction IDs\n"
        "💳 Card last 4 digits\n"
        "💰 Amount charged\n\n"
        "📧 **Email:** support@ecommerce.com\n"
        "📞 **Phone:** 1-800-123-456\n"
        "📌 **Response time:** Within 2 hours during business hours"
    )


def check_product_availability(query: str) -> str:
    """Check product stock and availability"""
    query_lower = query.lower()

    found_products = []
    for product_name, details in MOCK_PRODUCTS.items():
        if product_name in query_lower:
            found_products.append((product_name, details))

    if not found_products:
        return (
            "🔍 **Product Not Found**\n\n"
            "I couldn't find that product in our search.\n\n"
            "**Try:**\n"
            "• Using a different product name\n"
            "• Checking our categories on the homepage\n"
            "• Visiting the full product catalog\n\n"
            "**Can't find something specific?**\n"
            "📧 Tell us what you're looking for: support@ecommerce.com"
        )

    response = "📦 **Product Availability**\n\n"

    for product, details in found_products:
        stock_status = "✅ In Stock" if details["stock"] > 0 else "❌ Out of Stock"
        response += (
            f"**{product.title()}**\n"
            f"💵 Price: ₹{details['price']}\n"
            f"{stock_status} ({details['stock']} available)\n"
            f"⭐ Rating: {details['rating']}/5 ({details['reviews']} reviews)\n\n"
        )

    if any(details["stock"] == 0 for _, details in found_products):
        response += "💬 Out of stock? We'll notify you when it's back!"

    return response


def apply_discount_code(code: str = None, query: str = None) -> str:
    """Apply and validate discount codes"""
    if not code:
        return (
            "🎟️ **Coupon/Promo Codes**\n\n"
            "**Current Active Offers:**\n"
            "🏷️ **SAVE20** - 20% off (min ₹1,000)\n"
            "🏷️ **FLAT100** - ₹100 flat off (min ₹500)\n"
            "🏷️ **NEWUSER** - 50% off (min ₹2,000)\n\n"
            "**How to use:**\n"
            "1. Go to checkout\n"
            "2. Find 'Coupon Code' field\n"
            "3. Enter code and apply\n"
            "4. Discount shows instantly\n\n"
            "**Terms:**\n"
            "✓ One coupon per order\n"
            "✓ Valid on applicable categories\n"
            "✓ Cannot be combined\n"
            "✓ Limited time offers"
        )

    code_upper = code.upper()
    coupon = MOCK_COUPONS.get(code_upper)

    if not coupon:
        return (
            f"❌ **Code '{code}' Not Found**\n\n"
            "This coupon doesn't exist or has been removed.\n\n"
            "**Active codes right now:**\n"
            "• SAVE20 - 20% off\n"
            "• FLAT100 - ₹100 off\n"
            "• NEWUSER - 50% off (first purchase)"
        )

    if not coupon["valid"]:
        return (
            f"⏰ **Code '{code}' Expired**\n\n"
            "This coupon is no longer valid.\n\n"
            "Check our **'Offers'** page for active deals!"
        )

    return (
        f"✅ **Coupon Applied: {code}**\n\n"
        f"**Discount:** {coupon['discount']}{'%' if isinstance(coupon['discount'], float) else ''}\n"
        f"**Minimum Order:** ₹{coupon['min_amount']}\n\n"
        "Your discount will be applied at checkout!"
    )


def process_complaint(query: str) -> str:
    """Log and process customer complaints"""
    complaint_obj = {
        "id": f"CMP-{random.randint(10000, 99999)}",
        "query": query,
        "timestamp": datetime.now(),
        "status": "logged",
    }
    COMPLAINT_LOG.append(complaint_obj)

    logger.warning(f"Complaint logged: {complaint_obj['id']}")

    return (
        f"📝 **Complaint Logged**\n\n"
        f"**Ticket ID:** {complaint_obj['id']}\n\n"
        "We're sorry to hear about this. 😔\n\n"
        "**What we're doing:**\n"
        "✓ Your complaint has been recorded\n"
        "✓ Our team will review it shortly\n"
        "✓ You'll get updates via email/SMS\n\n"
        "**Expected response:** Within 4 hours\n\n"
        "**Need immediate help?**\n"
        "📞 Call: 1-800-123-456 (priority line)\n"
        "📧 Email: escalation@ecommerce.com"
    )


def get_product_recommendations(query: str) -> str:
    """Provide product recommendations based on query"""
    return (
        "🎁 **Recommended Products**\n\n"
        "Based on your interest, you might like:\n\n"
        "1. **Wireless Headphones** - ₹2,499\n"
        "   ⭐ 4.5/5 (230 reviews) | 45 in stock\n\n"
        "2. **Running Shoes** - ₹3,999\n"
        "   ⭐ 4.7/5 (150 reviews) | 12 in stock\n\n"
        "3. **Smart Watch** - ₹5,999\n"
        "   ⭐ 4.3/5 (89 reviews) | 8 in stock\n\n"
        "💡 **Pro tip:** All items have free shipping on orders ₹500+"
    )
