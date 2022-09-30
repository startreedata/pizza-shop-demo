# Pizza Shop Demo

This repository contains the code for the Pizza Shop Demo. 

![](images/architecture.png)

## Run the demo

```bash
docker-compose \
  -f docker-compose-base.yml \
  -f docker-compose-pinot.yml \
  -f docker-compose-dashboard-enriched.yml \
  up
```

Once that's run, you can navigate to the following:

* Pinot UI - http://localhost:9000
* Streamlit Dashboard - http://localhost:8502

You can find a deeper dive on each of the components at https://dev.startree.ai/docs/pinot/demo-apps/pizza-shop

## Things that sometimes don't work

The Kafka Streams component can get itself in a broken/stuck state if it tries to start before the Kafka topics exist. To fix that, restart the service:

```
docker restart kafka-streams
```

Less frequently, the `pinot-add-table` service never returns code 0 if it created one table and not the other. To stop that service, run this:

```
docker stop pinot-add-table
```
