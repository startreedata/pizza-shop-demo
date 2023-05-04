# Demo Script

```bash
docker-compose \
  -f docker-compose-base.yml \
  -f docker-compose-rwave.yml \
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

## Orders stream

```bash
rpk topic consume orders --brokers localhost:9092
rpk topic consume orders --brokers localhost:9092 | jq -c '.value | fromjson'
```

## Enrich stream

psql -h localhost -p 4566 -d dev -U root

## Apache Pinot - Orders Table

```bash
pygmentize -O style=github-dark pinot/config/schema.json
```

```bash
pygmentize -O style=github-dark pinot/config/table.json
```

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


## Kafka Streams - Joining products

```bash
kcat -C -b localhost:29092 -t products -c 10 -u | jq
```

```bash
pygmentize -O style=github-dark kafka-streams-quarkus/src/main/java/pizzashop/streams/TopologyProducer.java | less
```

```bash
kcat -C -b localhost:29092 -t enriched-order-items -c 10 -u | jq
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