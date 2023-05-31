# Pizza Shop Demo

This repository contains the code for the Pizza Shop Demo. 

![](images/architecture.png)

## Run the demo

```bash
docker-compose \
  -f docker-compose-base.yml \
  -f docker-compose-pinot.yml \
  -f docker-compose-rwave.yml \
  -f docker-compose-dashboard-enriched-quarkus.yml \
  up
```

```bash
docker-compose \
  -f docker-compose-base.yml \
  -f docker-compose-pinot-m1.yml \
  -f docker-compose-rwave.yml \
  -f docker-compose-dashboard-enriched-quarkus.yml \
  up
```

Once that's run, you can navigate to the following:

* Pinot UI - http://localhost:9000
* Streamlit Dashboard - http://localhost:8502

You can find a deeper dive on each of the components at https://dev.startree.ai/docs/pinot/demo-apps/pizza-shop
