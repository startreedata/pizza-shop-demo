# Demo Script

The Pizza Shop Demo shows how to build a real-time dashboard for the operators of a fictional pizza delivery service.

## Dependencies

* [kcat](https://docs.confluent.io/platform/current/app-development/kafkacat-usage.html) - produce, consume, and list topic and partition information for Kafka.
* [jq](https://stedolan.github.io/jq/) - Sed for JSON data

## Initial Architecture

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

