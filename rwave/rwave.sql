DROP SOURCE orders;

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

select * from orders LIMIT 5;

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

WITH orderItems AS (
    select unnest(items) AS orderItem, 
           id AS orderId, createdAt           
    FROM orders
)
SELECT orderId, createdAt,
       ((orderItem).productid, (orderItem).quantity, (orderItem).price)::
       STRUCT<productId varchar, quantity varchar, price varchar> AS orderItem,
        (products.id, products.name, products.description, products.category, products.image, products.price)::
        STRUCT<id varchar, name varchar, description varchar, category varchar, image varchar, price varchar> AS product
FROM orderItems
JOIN products ON products.id = (orderItem).productId
LIMIT 10

CREATE MATERIALIZED VIEW orderItems_view AS
WITH orderItems AS (
    select unnest(items) AS orderItem, 
           id AS orderId, createdAt           
    FROM orders
)
SELECT orderId, createdAt,
       ((orderItem).productid, (orderItem).quantity, (orderItem).price)::
       STRUCT<productId varchar, quantity varchar, price varchar> AS "orderItem",
        (products.id, products.name, products.description, products.category, products.image, products.price)::
        STRUCT<id varchar, name varchar, description varchar, category varchar, image varchar, price varchar> AS product
FROM orderItems
JOIN products ON products.id = (orderItem).productId;

CREATE SINK enrichedOrderItems_sink FROM orderItems_view 
WITH (
   connector='kafka',
   type='append-only',
   properties.bootstrap.server='redpanda:29092',
   topic='enriched-order-items'
);