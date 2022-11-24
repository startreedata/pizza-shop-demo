# Demo Script Commands to run

This is the demo for the Real-Time Analytics Stack Demo.

## Existing Architecture

```bash
docker exec -it mysql mysql -u mysqluser -p
```

```sql
select id, first_name, last_name, email, country 
FROM pizzashop.users 
LIMIT 5;
```

```sql
select id, name, category, price 
FROM pizzashop.products 
LIMIT 5;
```


```sql
exit
```

## RTA Architecture

```bash
kcat -C -b localhost:29092 -t orders -u | jq '.'
```

Open VS Code

* Show pinot/config/orders/schema.json
* Show pinot/config/orders/table.json

Open Pinot UI

```sql
select id, price, productsOrdered, status, totalQuantity, ts, userId 
from orders
limit 10
```
Back to the terminal

```bash
kcat -C -b localhost:29092 -t products -u | jq '.'
```

Open VS Code

* Show TopologyProducer.java

Back to terminal 

```bash
kcat -C -b localhost:29092 -t enriched-order-items -c1 | jq '.'
```

Open VS Code

* Show pinot/config/order_items_enriched/schema.json
* Show pinot/config/order_items_enriched/table.json

Back to Pinot UI

```sql
select * 
from order_items_enriched
LIMIT 10;
```

```sql
select "product.category" AS category, count(*)
FROM order_items_enriched
WHERE ts > ago('PT5M')
group by category
order by count(*) DESC
```

Open Streamlit

http://localhost:8502

* Change the amount of data being shown
* Change the refresh rate

Open VS Code

* Show app_enriched.py
