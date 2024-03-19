import random, time
from faker import Faker
from faker.providers import company
import json
import datetime
import uuid
import math
import os


# Generate fake users
fake = Faker()
users = []
for i in range(100):
    users.append(
        {
            "id": str(i),
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "email": fake.email(),
            "country": fake.country(),
        }
    )
print(users[:5])

# Get products
products = [json.loads(line) for line in open("products.jsonl", "r")]
print(products[:5])

product_prices = [(x["id"], float(x["price"])) for x in products]
print(product_prices[:5])

orders_to_generate = 1000
orders = []

while len(orders) < orders_to_generate:

    # Get a random a user and a product to order
    number_of_items = random.randint(1, 10)

    items = []
    for _ in range(0, number_of_items):
        product = random.choice(product_prices)
        user = random.choice(users)["id"]
        purchase_quantity = random.randint(1, 5)
        items.append(
            {
                "productId": str(product[0]),
                "quantity": purchase_quantity,
                "price": product[1],
            }
        )

    prices = [item["quantity"] * item["price"] for item in items]
    total_price = round(math.fsum(prices), 2)

    order_event = {
        "id": str(uuid.uuid4()),
        "createdAt": datetime.datetime.now().isoformat(),
        "userId": user,
        "status": "PLACED_ORDER",
        "price": total_price,
        "items": items,
    }

    orders.append(order_event)

# save to jsonl file
with open("orders.jsonl", "w") as file:
    for ord in orders:
        json_line = json.dumps(ord)
        file.write(json_line + "\n")
