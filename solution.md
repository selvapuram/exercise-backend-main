# Solution for Order Management System

## Problem Overview

In this task, we need to implement an API endpoint that handles the creation of orders for a stock exchange system. The solution should:

1. Accept order creation requests through a FastAPI endpoint.
2. Ensure that the order is stored in the database.
3. Place the order with an external stock exchange system (simulated in this case).
4. Return the appropriate HTTP status code and response based on whether the order was successfully placed.

### Requirements:

- **Endpoint**: The endpoint should accept the following fields in the request body:
    - `type` (string) — Order type (`"market"` or `"limit"`)
    - `side` (string) — Order side (`"buy"` or `"sell"`)
    - `instrument` (string) — A 12-character string identifying the instrument
    - `limit_price` (float) — Price for `limit` orders
    - `quantity` (integer) — Quantity of instruments to buy/sell

- **Validations**:
    - A `market` order should not have a `limit_price`.
    - A `limit` order must have a `limit_price`.

- **Database**: Orders should be stored in a database and saved through SQLAlchemy ORM.
- **Error Handling**:
    - A 201 status code should be returned for successfully created orders.
    - A 500 status code should be returned if the order fails to be placed on the stock exchange.
    - If the order fails during placement, the database transaction should be rolled back to ensure data consistency.

- **Test Cases**:
    - Ensure that the order is successfully stored in the database and placed on the stock exchange.
    - Verify both successful and unsuccessful responses (201 and 500 status codes).
    - Rollback database changes on failure.

---

## Solution Design

### 1. **FastAPI Endpoint** (`POST /orders`)

The core part of the solution is the FastAPI endpoint that handles the creation of orders. Here's a breakdown:

```python
@app.post("/orders", status_code=201, response_model=CreateOrderResponseModel)
async def create_order(model: CreateOrderModel, db: Session = Depends(get_db)):
    order_id = str(uuid4())
    created_at = datetime.utcnow()

    # Create an order instance for database storage
    db_order = OrderEntity(
        id=order_id,
        created_at=created_at,
        type=model.type_.value,
        side=model.side.value,
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
        id_=order_id,
        created_at=created_at,
        type_=model.type_,
        side=model.side,
        instrument=model.instrument,
        limit_price=model.limit_price,
        quantity=model.quantity,
    )

    # Place the order on the stock exchange
    try:
        place_order(order)
    except OrderPlacementError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error while placing the order")

    # Return the created order as the response
    response = CreateOrderResponseModel(
        id=order.id_,  
        created_at=order.created_at,
        type=order.type_,
        side=order.side,
        instrument=order.instrument,
        limit_price=order.limit_price,
        quantity=order.quantity,
    )
    return response

```
## 2. Database Interaction (SQLAlchemy)

The order is stored in a relational database using SQLAlchemy ORM. We define the `OrderEntity` as a model that maps to a table in the database. When a new order is created, it is added to the session and committed to the database. If an error occurs, the transaction is rolled back, ensuring the integrity of the database.

### Key Steps:
1. Define the `OrderEntity` model to map to a database table.
2. Create a new order instance and add it to the database session.
3. Commit the transaction to save the order.
4. If an error occurs while placing the order in the stock exchange, roll back the transaction to maintain consistency.

---

## 3. Validators and Error Handling

The `CreateOrderModel` has a root validator that checks the following:

- **Limit Price Validation**:
    - `limit_price` should **not** be provided for `market` orders.
    - `limit_price` **must** be provided for `limit` orders.

These validations ensure that the data meets the business rules before being saved to the database. If any of these rules are violated, a `ValueError` is raised, and a `422 Unprocessable Entity` status code is returned in the response.

### Validation Rules:
- **For Market Orders**: If `limit_price` is provided, it will trigger a validation error.
- **For Limit Orders**: If `limit_price` is missing, it will trigger a validation error.

---

## 4. Testing Strategy

To ensure that the application behaves as expected, several test cases have been defined to cover different scenarios:

### 4.1. Successful Order Creation
- **Test Case**: Valid input for a `limit` order.
- **Expected Behavior**:
    - The status code is `201` (Created).
    - The order is saved in the database.
    - The order is successfully placed on the stock exchange.

### 4.2. Invalid Order Creation (Limit Price Validation)
- **Test Case**: Invalid input where `limit_price` is provided for a `market` order.
- **Expected Behavior**:
    - The status code is `422` (Unprocessable Entity).
    - An appropriate error message is returned indicating that `limit_price` is prohibited for `market` orders.

### 4.3. Error Handling (Stock Exchange Failure)
- **Test Case**: Simulating a failure during the placement of the order on the stock exchange (e.g., random failure).
- **Expected Behavior**:
    - The status code is `500` (Internal Server Error).
    - The database transaction is rolled back.
    - The order is **not** placed in the stock exchange, and no order is saved in the database.

---

### Example Code for Testing:

```python
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

        # Fetch the order from the database using the (non-existing) ID
        order_id = response_data.get("id")
        if order_id:
            db_order = db.query(OrderEntity).filter(OrderEntity.id == order_id).first()
            assert db_order is None
        else:
            # Make sure no order exists at all
            db_order = db.query(OrderEntity).filter(OrderEntity.instrument == "AAPL12345678").first()
            assert db_order is None
```

# Bonus Task: Handling High Volume of Async Updates via Socket

## 1. **Asynchronous Processing with WebSockets**

- **WebSocket Integration:**
  - We will integrate WebSocket to receive real-time updates about order executions. WebSocket enables bidirectional communication between the client and server, allowing efficient transmission of messages. FastAPI provides support for WebSockets via the `WebSocket` class. :contentReference[oaicite:0]{index=0}

- **Handling Concurrent Updates:**
  - Given the high volume of updates, asynchronous background tasks will process updates and persist them in the database without blocking the main thread. These updates may include status changes, trade executions, and other critical order information. They need to be stored in the database and may trigger actions such as updating the order status or notifying the user.

## 2. **Database Changes for Async Updates**

- **Introducing Eventual Consistency:**
  - The system will operate in an eventually consistent manner, meaning updates might take some time before the database is fully updated. We can store updates in a queue or buffer before processing them to avoid overloading the database with frequent writes. This buffer could be implemented using a message queue like RabbitMQ or Redis to manage the updates.

- **Database Schema Update:**
  - To store execution information for orders, we may need to extend the database schema to include:
    - **OrderExecutionStatus:** A model that records the execution status of the order, including the order's execution progress, execution time, and any trade details.
    - **OrderHistory:** A model to track the history of changes for an order, including updates from the stock exchange.
  - These models can be linked to the `OrderEntity` model, creating a relationship between the updates and the original order.

## 3. **Asynchronous Background Tasks**

- **Background Processing:**
  - We can use FastAPI's Background Tasks or Celery to handle updates asynchronously. Celery is a powerful tool for managing distributed tasks, making it well-suited for handling high-volume updates. :contentReference[oaicite:1]{index=1}
  - A background task will:
    1. Process incoming updates from the socket connection.
    2. Update the order status or execution details in the database.
    3. Notify clients via WebSocket about the progress or completion of the order.

## 4. **Concurrency Handling and Rate Limiting**

- **Concurrency:**
  - The system will handle multiple WebSocket connections concurrently, as updates for many orders may arrive simultaneously. Using asyncio or FastAPI’s background task support allows processing each incoming update asynchronously without blocking the main application thread.

- **Rate Limiting:**
  - To prevent the system from being overwhelmed by too many updates in a short period, rate limiting will be implemented. This can be achieved by ensuring updates are processed in a controlled manner, either by limiting the number of updates per second or using a message queue to throttle the processing rate.

## 5. **Notification Mechanism for Clients**

- **Real-Time Client Notifications:**
  - In addition to updating the database, clients will be notified about the status of their orders in real-time. This can be achieved by sending WebSocket messages to clients whenever the order status is updated. Clients can subscribe to a specific order update channel, allowing the server to push updates to them as they occur.

- **Error Handling:**
  - Clients will be notified immediately in case of any errors during order execution. For example, if an order fails on the stock exchange, the WebSocket connection will send an error message indicating the issue.

## 6. **System Architecture Update**

- **Overall Flow:**
  1. **Client places an order** via HTTP (REST API).
  2. **WebSocket connection** is established with the stock exchange.
  3. As **updates** come in from the stock exchange:
    - Updates are stored in a buffer (queue).
    - Asynchronous background tasks process the updates.
    - The order status in the database is updated.
    - Clients are notified via WebSocket about the order status change.

- **Scalability Considerations:**
  - If the volume of orders grows, the system can be scaled by deploying it across multiple instances or using load balancers. Using a message queue ensures that updates can be processed in a distributed manner, allowing scaling of processing independently of the web application.

## 7. **Code Changes Overview**

- **WebSocket Endpoints:**
  - A new WebSocket endpoint will be added to receive order updates from the stock exchange. 
  - FastAPI's WebSocket support will be used for bidirectional communication.

    ```python
    from fastapi import FastAPI, WebSocket

    app = FastAPI()

    @app.websocket("/ws/orders/{order_id}")
    async def order_updates(websocket: WebSocket, order_id: str):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            # Process order updates
            await websocket.send_text(f"Update for order {order_id}: {data}")
    ```

- **Background Task Example:**
  - A background task will handle async order updates.

    ```python
    from fastapi import BackgroundTasks

    def process_order_update(order_id: str, update_data: dict):
        # Update the database with the new order information
        db_order = db.query(OrderEntity).filter(OrderEntity.id == order_id).first()
        db_order.execution_status = update_data["status"]
        db.commit()

    @app.post("/order-update")
    async def update_order(order_id: str, update_data: dict, background_tasks: BackgroundTasks):
        background_tasks.add_task(process_order_update, order_id, update_data)
         return {"message": "Update processing started"}
    ```
 
  - **Database Model for Execution Info:**
    ```python
    class OrderExecutionStatus(Base):
        __tablename__ = "order_execution_status"
        id = Column(Integer, primary_key=True, index=True)
        order_id = Column(String, ForeignKey("orders.id"))
        status = Column(String)
        execution_time = Column(DateTime, default=datetime.utcnow)
    ```
