# Demo Script

The Pizza Shop Demo shows how to build a real-time dashboard for the operators of a fictional pizza delivery service.

## Dependencies

* [kcat](https://docs.confluent.io/platform/current/app-development/kafkacat-usage.html) - produce, consume, and list topic and partition information for Kafka.
* [jq](https://stedolan.github.io/jq/) - Sed for JSON data

## Initial Architecture

Spin everything up on your machine:

```
docker-compose up
```

You can navigate to those Docker files to show how we're running each of the components.

We start with products and users loaded into a MySQL database. 
You can query those tables by connecting to the MySQL service:

```
docker exec -it mysql mysql -u mysqluser -p
```

The password is `mysqlpw`. 

```sql
SELECT name, description, category, price 
FROM pizzashop.products 
LIMIT 10;
```

```sql
SELECT id, first_name, last_name, email, country
FROM pizzashop.users 
LIMIT 10;
```

We also have a stream of orders in Apache Kafka.

```bash
kcat -C -b localhost:29092 -t orders | jq '.'
```

or 

```bash
kafkacat -C -b localhost:29092 -t orders | jq '.'
```

The code for the data generation is in [orders-service/multiseeder.py)(orders-service/multiseeder.py). 

## Adding Real-Time Analytics

We're going to put a Streamlit app on top of this data, but first we need to get a stream of the order items that contains all the product details.
We use Kafka Streams to do that and the code is in [TopologyProducer.java](kafka-streams-quarkus/src/main/java/pizzashop/streams/TopologyProducer.java)

We flat map the orders and key the resulting stream by product id, join that stream to the products stream, which results in the enriched stream.

Query the resulting stream:

```bash
kcat -C -b localhost:29092 -t enriched-order-items | jq '.'
```

or 

```bash
kafkacat -C -b localhost:29092 -t enriched-order-items | jq '.'
```

Both the `orders` and `enriched-order-items` are ingested into Apache Pinot.
You can find the config for the corresponding schema/table config in [pinot/config/orders](pinot/config/orders) and [pinot/config/order_items_enriched](pinot/config/order_items_enriched)

Navigate to http://localhost:9000 to demo the data in Pinot and write some ad hoc queries.
Below are some examples:

```sql
select count(*) FILTER(WHERE  ts > ago('PT1M')) AS events1Min,
    count(*) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS events1Min2Min,
    sum("price") FILTER(WHERE  ts > ago('PT1M')) AS total1Min,
    sum("price") FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS total1Min2Min
from orders
where ts > ago('PT2M')
limit 1
```


```sql
SELECT "product.name" AS product, 
        "product.image" AS image,
        distinctcount(orderId) AS orders,
        sum("orderItem.quantity") AS quantity
FROM order_items_enriched
where ts > ago('PT2M')
group by product, image
LIMIT 5
```

Streamlit is running at http://localhost:8502.
The code for Streamlit is at [streamlit/app_enriched.py](streamlit/app_enriched.py).