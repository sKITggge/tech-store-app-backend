PROMO_CODES: dict[str, int] = {
    "SAVE10": 10,
}


def get_discount_percentage(code: str) -> int:
    return PROMO_CODES.get(code.strip().upper(), 0)
