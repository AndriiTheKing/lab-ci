from unittest.mock import Mock

import pytest

from shop.cart import Cart, Item

# ---------- add / items_count ----------


def test_new_cart_is_empty(cart: Cart) -> None:
    assert cart.items_count() == 0
    assert cart.total() == 0


def test_add_single_item(cart: Cart) -> None:
    cart.add("book", price=200.0)
    assert cart.items_count() == 1
    assert cart.total() == 200.0


def test_items_count_sums_quantities(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_add_same_item_twice_increases_qty(cart: Cart) -> None:
    cart.add("book", price=200.0, qty=2)
    cart.add("book", price=200.0, qty=3)
    assert cart.items_count() == 5
    assert cart.total() == 1000.0


def test_add_same_name_with_different_price_keeps_first_price(cart: Cart) -> None:
    # Рішення: ціна першого додавання зберігається, змінюється лише кількість.
    cart.add("book", price=200.0)
    cart.add("book", price=999.0)
    assert cart.items_count() == 2
    assert cart.total() == 400.0


# ---------- remove ----------


def test_remove_existing_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("book")
    assert cart_with_items.items_count() == 4
    assert cart_with_items.total() == 60.0


# ---------- винятки ----------


def test_add_negative_price_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        cart.add("book", price=-1.0)


@pytest.mark.parametrize("qty", [0, -1, -100])
def test_add_non_positive_qty_raises(cart: Cart, qty: int) -> None:
    with pytest.raises(ValueError, match="qty"):
        cart.add("book", price=10.0, qty=qty)


def test_remove_missing_item_raises(cart: Cart) -> None:
    with pytest.raises(KeyError):
        cart.remove("ghost")


@pytest.mark.parametrize("discount", [-0.1, -10, 100.1, 150])
def test_total_invalid_discount_raises(cart_with_items: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart_with_items.total(discount_percent=discount)


# ---------- total (параметризація, граничні значення) ----------


@pytest.mark.parametrize(
    ("discount", "expected"),
    [(0, 400.0), (10, 360.0), (50, 200.0), (100, 0.0)],
)
def test_total_discounts(cart: Cart, discount: float, expected: float) -> None:
    cart.add("book", price=200.0, qty=2)
    assert cart.total(discount_percent=discount) == expected


def test_total_is_rounded_to_two_decimals(cart: Cart) -> None:
    cart.add("thing", price=0.1)
    cart.add("other", price=0.2)
    assert cart.total() == pytest.approx(0.3)
    assert cart.total(discount_percent=33.333) == pytest.approx(0.2, abs=0.01)


# ---------- total_in (тестовий дублер) ----------


def test_total_in_usd(cart: Cart, rates: Mock) -> None:
    cart.add("book", price=400.0)
    assert cart.total_in("USD", rates) == 10.0
    rates.get_rate.assert_called_once_with("USD")


@pytest.mark.parametrize("bad_rate", [0, -5.0])
def test_total_in_invalid_rate_raises(cart_with_items: Cart, bad_rate: float) -> None:
    provider = Mock()
    provider.get_rate.return_value = bad_rate
    with pytest.raises(ValueError, match="rate"):
        cart_with_items.total_in("USD", provider)


class FakeRates:
    """Власна заглушка (stub) без жодних мережевих запитів."""

    def get_rate(self, currency: str) -> float:
        return {"USD": 40.0, "EUR": 50.0}[currency]


def test_total_in_with_fake_provider(cart_with_items: Cart) -> None:
    assert cart_with_items.total_in("EUR", FakeRates()) == 9.2


# ---------- TDD: most_expensive ----------


def test_most_expensive_empty_cart_returns_none(cart: Cart) -> None:
    assert cart.most_expensive() is None


def test_most_expensive_returns_item_with_highest_unit_price(cart_with_items: Cart) -> None:
    result = cart_with_items.most_expensive()
    assert result == Item("book", 200.0, 2)


def test_most_expensive_uses_unit_price_not_line_total(cart: Cart) -> None:
    cart.add("pen", price=15.0, qty=100)  # рядок = 1500, але ціна одиниці низька
    cart.add("book", price=200.0, qty=1)
    result = cart.most_expensive()
    assert result is not None
    assert result.name == "book"
