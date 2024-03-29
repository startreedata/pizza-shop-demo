# Demo Script Commands to Run

This is the demo for the Real-Time Analytics Stack Demo.

## Existing Architecture

To connect to the MySQL database, run:

```bash
docker exec -it mysql mysql -u mysqluser -p
```

Execute the following SQL queries to view sample data:

```sql
select id, first_name, last_name, email, country
FROM pizzashop.users LIMIT 5;
```

```sql
select id, name, category, price
FROM pizzashop.products LIMIT 5;
```

Exit the MySQL prompt:

```sql
exit
```

## RTA Architecture

Consume messages from the `orders` topic using kcat:

```bash
kcat -C -b localhost:29092 -t orders -u | jq '.'
```

View configuration files using a generic editor or `cat` command:

```bash
cat ../pinot/config/orders/schema.json | jq
```

```bash
cat ../pinot/config/orders/table.json | jq
```

Access the Pinot UI and execute the following SQL query:

```sql
select id, price, productsOrdered, status, totalQuantity, ts, userId
from orders limit 10
```

Return to the terminal and consume messages from the `products` topic:

```bash
kcat -C -b localhost:29092 -t products -u | jq '.'
```

View the `TopologyProducer.java` file:

```bash
cat TopologyProducer.java
```

Back in the terminal, consume a single message from the `enriched-order-items` topic:

```bash
kcat -C -b localhost:29092 -t enriched-order-items -c1 | jq '.'
```

View the configuration files for enriched order items:

```bash
cat ../pinot/config/order_items_enriched/schema.json | jq
```

```bash
cat ../pinot/config/order_items_enriched/table.json | jq
```

Switch to the Pinot UI and execute the following SQL queries:

```sql
select *
from order_items_enriched LIMIT 10;
```

```sql
select "product.category" AS category, count(*)
FROM order_items_enriched
WHERE ts > ago('PT5M')
group by category
order by count(*) DESC
```

Open the Streamlit dashboard at [http://localhost:8502](http://localhost:8502):

- Change the amount of data being shown.
- Change the refresh rate.

Finally, review the Streamlit app code:

```bash
cat app_enriched.py
```
