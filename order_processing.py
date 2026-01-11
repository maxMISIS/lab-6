DEFAULT_CURRENCY = "USD"

TAX_RATE = 0.21

COUPON_SAVE10 = "SAVE10"
COUPON_SAVE20 = "SAVE20"
COUPON_VIP = "VIP"

SAVE10_RATE = 0.10
SAVE20_RATE = 0.20
SAVE20_MIN_SUBTOTAL = 200
SAVE20_ELSE_RATE = 0.05

VIP_DISCOUNT_DEFAULT = 50
VIP_DISCOUNT_SMALL = 10
VIP_SMALL_SUBTOTAL_LIMIT = 100

ORDER_SUFFIX = "X"


def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def _ensure_required(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        return DEFAULT_CURRENCY
    return currency


def _validate_items(items):
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for it in items:
        if "price" not in it or "qty" not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")


def _calc_subtotal(items):
    subtotal = 0
    for it in items:
        subtotal = subtotal + it["price"] * it["qty"]
    return subtotal


def _calc_discount(subtotal, coupon):
    if coupon is None or coupon == "":
        return 0

    if coupon == COUPON_SAVE10:
        return int(subtotal * SAVE10_RATE)

    if coupon == COUPON_SAVE20:
        if subtotal >= SAVE20_MIN_SUBTOTAL:
            return int(subtotal * SAVE20_RATE)
        return int(subtotal * SAVE20_ELSE_RATE)

    if coupon == COUPON_VIP:
        if subtotal < VIP_SMALL_SUBTOTAL_LIMIT:
            return VIP_DISCOUNT_SMALL
        return VIP_DISCOUNT_DEFAULT

    raise ValueError("unknown coupon")


def _calc_total_after_discount(subtotal, discount):
    total_after_discount = subtotal - discount
    if total_after_discount < 0:
        total_after_discount = 0
    return total_after_discount


def _calc_tax(amount):
    return int(amount * TAX_RATE)


def _make_order_id(user_id, items_count):
    return str(user_id) + "-" + str(items_count) + "-" + ORDER_SUFFIX


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    currency = _ensure_required(user_id, items, currency)
    _validate_items(items)

    subtotal = _calc_subtotal(items)
    discount = _calc_discount(subtotal, coupon)

    total_after_discount = _calc_total_after_discount(subtotal, discount)
    tax = _calc_tax(total_after_discount)
    total = total_after_discount + tax

    items_count = len(items)
    order_id = _make_order_id(user_id, items_count)

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": items_count,
    }