# Demo Script

```bash
docker-compose \
  -f docker-compose-base.yml \
  -f docker-compose-pinot.yml \
  -f docker-compose-rwave.yml \
  -f docker-compose-dashboard.yml \
  -f docker-compose-dashboard-enriched-only.yml \
  up
```

## MySQL

```bash
docker exec -it mysql mysql -u mysqluser -p
```

```sql
use pizzashop;
show tables;
```

```sql
select * from users LIMIT 10;
select * from products LIMIT 5;
```

## Orders stream

```bash
rpk topic consume orders --brokers localhost:9092
rpk topic consume orders --brokers localhost:9092 | jq -c '.value | fromjson'
```

Navigate to http://localhost:8080 for the RedPanda UI

## Apache Pinot - Orders Table

```bash
pygmentize -O style=github-dark pinot/config/schema.json
```

```bash
pygmentize -O style=github-dark pinot/config/table.json
```

Navigate to http://localhost:9000

```python
from pinotdb import connect
import pandas as pd
import os

pinot_host=os.environ.get("PINOT_SERVER", "localhost")
pinot_port=os.environ.get("PINOT_PORT", 8099)
conn = connect(pinot_host, pinot_port)

query = """
select count(*) FILTER(WHERE  ts > ago('PT1M')) AS events1Min,
       count(*) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS events1Min2Min,
       sum(price) FILTER(WHERE  ts > ago('PT1M')) AS total1Min,
       sum(price) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS total1Min2Min
from orders 
where ts > ago('PT2M')
limit 1
"""

curs = conn.cursor()
curs.execute(query)
df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
```

## Streamlit - Basic dashboard

```bash
pygmentize -O style=github-dark streamlit/app.py | less
```

Navigate to http://localhost:8501


## RisingWave - Joining products

```bash
rpk topic consume products --brokers localhost:9092 | jq -c '.value | fromjson'
```

Enrich stream:

```
psql -h localhost -p 4566 -d dev -U root
```

Create sources

```sql
CREATE SOURCE IF NOT EXISTS orders (
    id varchar,
    createdAt TIMESTAMP,
    userId integer,
    status varchar,
    price double,
    items STRUCT <
      productId varchar,
      quantity integer,
      price double
    >[]
)
WITH (
   connector='kafka',
   topic='orders',
   properties.bootstrap.server='redpanda:29092',
   scan.startup.mode='earliest',
   scan.startup.timestamp_millis='140000000'
)
ROW FORMAT JSON;

CREATE SOURCE IF NOT EXISTS products (
    id varchar,
    name varchar,
    description varchar,
    category varchar,
    price double,
    image varchar
)
WITH (
   connector='kafka',
   topic='products',
   properties.bootstrap.server='redpanda:29092',
   scan.startup.mode='earliest',
   scan.startup.timestamp_millis='140000000'
)
ROW FORMAT JSON;
```

Create materialized view

```sql
CREATE MATERIALIZED VIEW orderItems_view AS
WITH orderItems AS (
    select unnest(items) AS orderItem, 
           id AS "orderId", createdAt           
    FROM orders
)
SELECT "orderId", createdAt,
       ((orderItem).productid, (orderItem).quantity, (orderItem).price)::
       STRUCT<productId varchar, quantity varchar, price varchar> AS "orderItem",
        (products.id, products.name, products.description, products.category, products.image, products.price)::
        STRUCT<id varchar, name varchar, description varchar, category varchar, image varchar, price varchar> AS product
FROM orderItems
JOIN products ON products.id = (orderItem).productId;
```

Create sink

```sql
CREATE SINK enrichedOrderItems_sink FROM orderItems_view 
WITH (
   connector='kafka',
   type='append-only',
   properties.bootstrap.server='redpanda:29092',
   topic='enriched-order-items'
);
```

```bash
rpk topic consume enriched-order-items --brokers localhost:9092 | jq -c '.value | fromjson'
```

## Apache Pinot - Enriched Order Items Table


```bash
pygmentize -O style=github-dark pinot/config/order_items_enriched/schema.json | less
```

```bash
pygmentize -O style=github-dark pinot/config/order_items_enriched/table.json | less
```

## Streamlit - Enriched dashboard

```bash
pygmentize -O style=github-dark streamlit/app_enriched.py | less
```

Navigate to http://localhost:8502
