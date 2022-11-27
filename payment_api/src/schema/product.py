"""Product models."""

from typing import Literal

from schema.mixins import OrjsonModel


class ProductData(OrjsonModel):
    """Product info."""
    name: str
    description: str


class Product(OrjsonModel):
    """Payment product info."""
    unit_amount: int
    currency: Literal['usd']
    product_data: ProductData
