import pytest
from pydantic import ValidationError
from app.api import CreateOrderModel
from app.types import OrderType


def test_market_order_with_limit_price():
    # Test case where a market order is provided with a limit_price (invalid)
    with pytest.raises(ValidationError) as exc_info:
        CreateOrderModel(
            type="market",  # type 'market'
            side="buy",
            instrument="AAPL12345678",
            limit_price=150.0,  # limit_price should not be present for market orders
            quantity=10,
        )

    # Check if the error message contains the expected validation message
    assert "Providing a `limit_price` is prohibited for type `market`" in str(exc_info.value)


def test_limit_order_without_limit_price():
    # Test case where a limit order is provided without a limit_price (invalid)
    with pytest.raises(ValidationError) as exc_info:
        CreateOrderModel(
            type="limit",  # type 'limit'
            side="buy",
            instrument="AAPL12345678",
            limit_price=None,  # limit_price is required for limit orders
            quantity=10,
        )

    # Check if the error message contains the expected validation message
    assert "Attribute `limit_price` is required for type `limit`" in str(exc_info.value)


def test_valid_limit_order_with_limit_price():
    # Test case where a limit order is provided with a valid limit_price (valid)
    order = CreateOrderModel(
        type="limit",  # type 'limit'
        side="buy",
        instrument="AAPL12345678",
        limit_price=150.0,  # limit_price is valid for limit orders
        quantity=10,
    )

    # If no validation error occurs, this will pass the test
    assert order.limit_price == 150.0
    assert order.type_ == OrderType.LIMIT


def test_valid_market_order_without_limit_price():
    # Test case where a market order is provided without a limit_price (valid)
    order = CreateOrderModel(
        type="market",  # type 'market'
        side="buy",
        instrument="AAPL12345678",
        limit_price=None,  # limit_price should be None for market orders
        quantity=10,
    )

    # If no validation error occurs, this will pass the test
    assert order.limit_price is None
    assert order.type_ == OrderType.MARKET
