from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, condecimal, conint, constr, root_validator
from sqlalchemy.orm import Session

from app.types import Order, OrderSide, OrderType
from app.database import get_db, OrderEntity
from app.stock_exchange import place_order, OrderPlacementError

app = FastAPI()


class CreateOrderModel(BaseModel):
    type_: OrderType = Field(..., alias="type")
    side: OrderSide
    instrument: constr(min_length=12, max_length=12)
    limit_price: Optional[condecimal(decimal_places=2)]
    quantity: conint(gt=0)

    @root_validator(pre=True)
    def validator(cls, values: dict):
        order_type = values.get("type")
        limit_price = values.get("limit_price")

        if order_type == OrderType.MARKET.value and limit_price is not None:
            raise ValueError(
                "Providing a `limit_price` is prohibited for type `market`"
            )

        if order_type == OrderType.LIMIT.value and limit_price is None:
            raise ValueError("Attribute `limit_price` is required for type `limit`")

        return values


class CreateOrderResponseModel(Order):
    pass


@app.post(
    "/orders",
    status_code=201,
    response_model=CreateOrderResponseModel,
    response_model_by_alias=True,
)
async def create_order(model: CreateOrderModel, db: Session = Depends(get_db)):
    order_id = str(uuid4())
    created_at = datetime.utcnow()

    # Create an order instance for database storage
    db_order = OrderEntity(
        id=order_id,
        created_at=created_at,
        type=model.type_.value,  # Ensure type is properly set from enum
        side=model.side.value,  # Ensure side is properly set from enum
        instrument=model.instrument,
        limit_price=model.limit_price,
        quantity=model.quantity,
    )

    # Save to the database
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create an Order instance for stock exchange
    order = Order(
        id=order_id,  # Use 'id_' as required by the Order model
        created_at=created_at,
        type=model.type_,  # Use 'type_' as required by the Order model
        side=model.side,  # 'side' can be passed as-is
        instrument=model.instrument,
        limit_price=model.limit_price,
        quantity=model.quantity,
    )

    # Place the order on the stock exchange
    try:
        place_order(order)
    except OrderPlacementError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error while placing the order"},
        )

    # Return the created order as the response model, Pydantic handles aliasing
    return order
