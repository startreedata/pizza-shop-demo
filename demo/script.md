# Demo Script

The Pizza Shop Demo shows how to build a real-time dashboard for the operators of a fictional pizza delivery service.

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
Install kcat on your machine to make it easier to query 

```bash
kcat -C -b localhost:29092 -t orders
```

or 

```bash
kafkacat -C -b localhost:29092 -t orders -c 10
```