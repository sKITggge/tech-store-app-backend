from enum import StrEnum


class UserRole(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class Order(StrEnum):
    asc = "asc"
    desc = "desc"


class SortBy(StrEnum):
    title = "title"
    price = "price"
