"""Test data for SauceDemo. These are the public demo accounts listed on the login page."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

PASSWORD = "secret_sauce"


@dataclass(frozen=True)
class User:
    username: str
    password: str = PASSWORD


STANDARD_USER = User("standard_user")
LOCKED_OUT_USER = User("locked_out_user")
PROBLEM_USER = User("problem_user")
PERFORMANCE_GLITCH_USER = User("performance_glitch_user")
ERROR_USER = User("error_user")
VISUAL_USER = User("visual_user")

USERS_THAT_CAN_LOG_IN = [
    STANDARD_USER,
    PROBLEM_USER,
    PERFORMANCE_GLITCH_USER,
    ERROR_USER,
    VISUAL_USER,
]


class SortOption(StrEnum):
    NAME_ASC = "Name (A to Z)"
    NAME_DESC = "Name (Z to A)"
    PRICE_ASC = "Price (low to high)"
    PRICE_DESC = "Price (high to low)"


class Product(StrEnum):
    BACKPACK = "Sauce Labs Backpack"
    BIKE_LIGHT = "Sauce Labs Bike Light"
    BOLT_TSHIRT = "Sauce Labs Bolt T-Shirt"
    FLEECE_JACKET = "Sauce Labs Fleece Jacket"
    ONESIE = "Sauce Labs Onesie"
    RED_TSHIRT = "Test.allTheThings() T-Shirt (Red)"

    @property
    def slug(self) -> str:
        """The id fragment SauceDemo derives from a product name, e.g. ``sauce-labs-backpack``."""
        return self.value.lower().replace(" ", "-")


@dataclass(frozen=True)
class Customer:
    first_name: str = "Ada"
    last_name: str = "Lovelace"
    postal_code: str = "10115"


TAX_RATE = 0.08
