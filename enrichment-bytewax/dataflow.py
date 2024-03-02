import json
import os

from bytewax import operators as op
from bytewax.connectors.kafka import KafkaSinkMessage, operators as kop
from bytewax.dataflow import Dataflow

# Read environment variables
orders_topic = os.getenv('ORDERS_TOPIC', 'orders')
products_topic = os.getenv('PRODUCTS_TOPIC', 'products')
enriched_order_items_topic = os.getenv('ENRICHED_ORDER_ITEMS_TOPIC', 'enriched-order-items')
brokers = os.getenv('BROKERS').split(',')


def extract_items(x):
    json_value = json.loads(x.value)

    result = []
    for item in json_value["items"]:
        order_item_with_context = {
            "orderId": json_value["id"],
            "orderItem": item,
            "createdAt": json_value["createdAt"]
        }
        result.append(KafkaSinkMessage(item["productId"], json.dumps(order_item_with_context)))
    return result


flow = Dataflow("test")
in_orders = kop.input("kafka-in-orders", flow, brokers=brokers, topics=[orders_topic])
in_products = kop.input("kafka-in-products", flow, brokers=brokers, topics=[products_topic])

processed = op.flat_map("flat_map", in_orders.oks, extract_items)
op.inspect("out", processed)
kop.output("kafka-out", processed, brokers=brokers, topic=enriched_order_items_topic)
