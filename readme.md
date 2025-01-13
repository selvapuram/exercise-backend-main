# Backend engineering task

### Intro 

The repository contains a bare setup for a REST API to place orders via a `POST - /orders` request, it can be found in [./app/api.py](./app/api.py).
Additionally, it contains [a building block](./app/stock_exchange.py) that symbolizes placing an order at the stock exchange.

The folder [tests](./tests) contains the setup for tests with the framework pytest.

The challenge in this repository is a simplified version of what we are dealing with at lemon.markets 🍋. 

## Your task

We would like you to finalize the missing parts in this repository so that the following requirements are fulfilled:
1. a valid request to `POST /orders` should result in the order being stored in a database of your choice.
2. the created order should be placed at the stock exchange (use the method `place_order` provided in stock_exchange.py)
3. the endpoint should return a status code of 201 and the created order details, in case that: the order has been saved in the database **AND** it is **guaranteed** that the order is being placed on the stock exchange.  
4. in case of an error in the endpoint it should return the status code 500 and the body `{"message": "Internal server error while placing the order"}` 
5. the API should be highly scalable and reliable. The reliability of the provided stock exchange should not impact the reliability of the `POST /orders` endpoint


Additionally, please add some tests and document how you would test the application as a whole and its pieces.
For the implementation you can choose to use this Python setup or implement it in Javascript/Typescript.

Please include a `solution.md` file where you document your decisions, assumptions, and also improvements you would like to incorporate in the future.

We value your time ⏰, so we do not expect you to spend more than 4 hours preparing the solution. 🤗 
Focus on implementing the main task first and afterwards jump on additional improvements as you see fit.

### Bonus tasks
* How would you change the system if we would receive a high volume of async updates to the orders placed through a socket connection on the stock exchange, e.g. execution information? Please outline the changes in the `solution.md`.
* Feel free to add a GitHub actions workflow to test the application.
* Feel free to add a Dockerfile.

## Code quality

In order to keep a certain amount of code quality, we are using pre-commit hooks
in this repository, which are installed by a 3rd-party tool called [pre-commit](https://pre-commit.com/).

Please follow [this documentation](https://pre-commit.com/#install) to install `pre-commit`
on your local machine. After that just execute the following command to install the hooks
to your git folder:

```shell
pre-commit install
```


###  Everything process related
Please create a fork or clone of this repository, commit all of your work to a new branch, and provide us with a link to the solution via mail 📩, at least 6h before the review meeting.
