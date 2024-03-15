import os
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

import orjson
from bytewax import operators as op
from bytewax.connectors.kafka import (
    KafkaSinkMessage,
    KafkaSourceMessage,
    operators as kop,
)
from bytewax.dataflow import Dataflow


# define product dataclass
@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    category: str
    image: str


def load_products(file_path: str) -> Dict[int, Product]:
    products = {}
    with open(file_path, "r") as file:
        for line in file:
            data = orjson.loads(line)
            product = Product(
                id=str(data.get("id", 0)),  # Provide default values if key is missing
                name=data.get("name", "Unknown"),
                description=data.get("description", "No description"),
                price=data.get("price", "0"),
                category=data.get("category", "Unknown category"),
                image=data.get("image", "No image available"),
            )
            products[product.id] = product
    return products


@dataclass
class OrderItemWithContext:
    id: str
    item: str
    createdAt: str


orders_topic = os.getenv("ORDERS_TOPIC", "orders")
enriched_order_items_topic = os.getenv("ENRICHED_ORDERS_TOPIC", "enriched-order-items")
brokers = os.getenv("BOOTSTRAP_SERVERS", "[localhost:29092]").split(",")


def extract_items(msg: KafkaSourceMessage) -> List:
    json_value = orjson.loads(msg.value)

    result = []
    for item in json_value["items"]:
        order_item_with_context = OrderItemWithContext(
            id=json_value["id"], item=item, createdAt=json_value["createdAt"]
        )
        result.append((item["productId"], order_item_with_context))
    return result


def enrich_items(
    products: Dict[int, Product],
    product_id__order_item: Tuple[str, OrderItemWithContext],
) -> KafkaSinkMessage:
    product_id, order_item = product_id__order_item
    product = products[product_id]
    result = {
        "orderId": order_item.id,
        "orderItem": order_item.item,
        "createdAt": order_item.createdAt,
        "product": product,
    }
    return KafkaSinkMessage(product_id.encode(), orjson.dumps(result))


flow = Dataflow("product-enrichment")
in_orders = kop.input("kafka-in-orders", flow, brokers=brokers, topics=[orders_topic])

# Inspect errors and crash
op.inspect("inspect-kafka-errors", in_orders.errs).then(op.raises, "kafka-error")
op.inspect("inspect-items", in_orders.oks)

# Expand order into items
items = op.flat_map("flat_map", in_orders.oks, extract_items)

# enrich items with product data
products = load_products("data/products.jsonl")
enriched = op.map("enrich", items, lambda order: enrich_items(products, order))

op.inspect("out", enriched)
kop.output("kafka-out", enriched, brokers=brokers, topic=enriched_order_items_topic)
