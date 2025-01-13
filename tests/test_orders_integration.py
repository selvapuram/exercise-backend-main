import pytest
from uuid import uuid4
from app.database import OrderEntity


def test_create_order(client, db):
    response = client.post(
        "/orders",
        json={
            "type": "limit",
            "side": "buy",
            "instrument": "AAPL12345678",
            "limit_price": 150.0,
            "quantity": 10,
        },
    )

    if response.status_code == 201:
        # Assert that 'id' is present in the response
        response_data = response.json()
        assert "id" in response_data

        # Fetch the order from the database using the ID
        order_id = response_data["id"]
        db_order = db.query(OrderEntity).filter(OrderEntity.id == order_id).first()

        # Assert that the order exists in the database
        assert db_order is not None
        assert db_order.id == order_id
        assert db_order.type == "limit"
        assert db_order.instrument == "AAPL12345678"
        assert db_order.quantity == 10

    elif response.status_code == 500:
        # Assert that 'id' is not in the response
        response_data = response.json()
        assert "id" not in response_data

        response_data = response.json()
        assert response_data["message"] == "Internal server error while placing the order"

        # Fetch the order from the database using the (non-existing) ID
        order_id = response_data.get("id")
        if order_id:  # This is just a precaution, but it shouldn't be necessary.
            db_order = db.query(OrderEntity).filter(OrderEntity.id == order_id).first()
            assert db_order is None
        else:
            # Make sure no order exists at all (as we expect a failure at 500)
            db_order = db.query(OrderEntity).filter(OrderEntity.instrument == "AAPL12345678").first()
            assert db_order is None


def test_create_order_invalid(client):
    response = client.post(
        "/orders",
        json={
            "type": "market",
            "side": "sell",
            "instrument": "AAPL12345678",
            "limit_price": 150.0,  # Invalid for market order
            "quantity": 10,
        },
    )
    assert response.status_code == 422
