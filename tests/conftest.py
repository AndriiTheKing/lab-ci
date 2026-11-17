from unittest.mock import Mock

import pytest

from shop.cart import Cart


@pytest.fixture
def cart() -> Cart:
    """Порожній кошик."""
    return Cart()


@pytest.fixture
def cart_with_items() -> Cart:
    """Кошик: 2 книги по 200 грн і 4 ручки по 15 грн (разом 460 грн, 6 шт.)."""
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    cart.add("pen", price=15.0, qty=4)
    return cart


@pytest.fixture
def rates() -> Mock:
    """Заглушка RateProvider: 1 USD = 40 UAH."""
    provider = Mock()
    provider.get_rate.return_value = 40.0
    return provider
