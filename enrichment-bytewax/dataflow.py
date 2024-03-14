import json
import os
from dataclasses import dataclass
from typing import Dict, Any

import orjson
from bytewax import operators as op
from bytewax.connectors.kafka import KafkaSinkMessage, operators as kop
from bytewax.connectors.kafka.serde import SchemaDeserializer
from bytewax.dataflow import Dataflow


@dataclass
class OrderItemWithContext:
    id: str
    item: str
    createdAt: str


orders_topic = os.getenv('ORDERS_TOPIC', 'orders')
products_topic = os.getenv('PRODUCTS_TOPIC', 'products')
enriched_order_items_topic = os.getenv('ENRICHED_ORDERS_TOPIC', 'enriched-order-items')

brokers = os.getenv('BOOTSTRAP_SERVERS', '[localhost:29092]').split(',')


def extract_items(x):
    json_value = json.loads(x.value)

    result = []
    for item in json_value["items"]:
        order_item_with_context = OrderItemWithContext(
            id=json_value["id"],
            item=item,
            createdAt=json_value["createdAt"]
        )
        result.append((item["productId"], order_item_with_context))
    return result


def to_kafka_sink_message(x):
    order = x[1].get("order")
    product = x[1].get("product")
    if order is None or product is None:
        pass
    else:
        result = {
            "orderId": order.id,
            "orderItem": order.item,
            "createdAt": order.createdAt,
            "product": product.value
        }
        return KafkaSinkMessage(x[0], json.dumps(result))


class KeyDeserializer(SchemaDeserializer[bytes, str]):
    def de(self, obj: bytes) -> str:
        return str(obj)


class JSONDeserializer(SchemaDeserializer[bytes, Dict]):
    def de(self, obj: bytes) -> Dict[Any, Any]:
        return orjson.loads(obj)


flow = Dataflow("product-enrichment")
in_orders = kop.input("kafka-in-orders",
                      flow,
                      brokers=brokers,
                      topics=[orders_topic])

in_products = kop.input("kafka-in-products",
                        flow,
                        brokers=brokers,
                        topics=[products_topic])

items = op.flat_map("flat_map", in_orders.oks, extract_items)

val_de = JSONDeserializer()
key_de = KeyDeserializer()

json_products = kop.deserialize(
    "load_json", in_products.oks, key_deserializer=key_de, val_deserializer=val_de
)

keyed_products = op.key_on("key_on_identifier", json_products.oks, lambda x: x.value["id"])

# not sure if there is a point to use join_named at all given that I have to transform it anyway, consult TopologyProducer.java to see the expected outcome
joined = op.join_named("join", running=True, product=keyed_products, order=items)

op.inspect("joined", joined)
res = op.filter_map("transform", joined, to_kafka_sink_message)

op.inspect("out", res)
kop.output("kafka-out",
           res,
           brokers=brokers,
           topic=enriched_order_items_topic)
