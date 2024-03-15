from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

import orjson
from bytewax import operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink
from bytewax.testing import TestingSource


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
                id=str(data.get("id", 0)), 
                name=data.get("name", "Unknown"),
                description=data.get("description", "No description"),
                price=data.get("price", "0"),
                category=data.get("category", "Unknown category"),
                image=data.get("image", "No image available"),
            )
            products[product.id] = product
    return products


# define order item dataclass
@dataclass
class OrderItemWithContext:
    id: str
    item: str
    createdAt: str


# take an order and return a list of items
def extract_items(orders: bytes) -> List:
    json_value = orjson.loads(orders)

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
) -> str:
    product_id, order_item = product_id__order_item
    product = products[product_id]
    result = {
        "orderId": order_item.id,
        "orderItem": order_item.item,
        "createdAt": order_item.createdAt,
        "product": product,
    }
    return orjson.dumps(result)


flow = Dataflow("product-enrichment")
in_orders = op.input(
    "testing-in-orders",
    flow,
    TestingSource([line for line in open("data/orders.jsonl", "r")]),
)
op.inspect("orders", in_orders)
items = op.flat_map("flat_map", in_orders, extract_items)

products = load_products("data/products.jsonl")
enriched = op.map("enrich", items, lambda order: enrich_items(products, order))

op.inspect("joined", enriched)
op.output("print-out", enriched, StdOutSink())
