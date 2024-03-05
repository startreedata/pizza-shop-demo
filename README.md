# Pizza Shop Demo

This repository contains the code for the Pizza Shop Demo.

![](images/architecture.png)

## Run the demo

```bash
make 
```

Once that's run, you can navigate to the following:

* Pinot UI — http://localhost:9000
* Streamlit Dashboard — http://localhost:8502

You can find a deeper dive on each of the components at https://dev.startree.ai/docs/pinot/demo-apps/pizza-shop

## Things that sometimes don't work

Less frequently, the `pinot-add-table` service never returns code 0 if it created one table and not the other. To stop that service, run this:

```
docker stop pinot-add-table
```

## Stop everything

```bash
make stop
```


