# Bytewax Enrichment

This directory contains files to enrich the stream of items contained in each order. It also contains a dataflow (`dataflow_pre.py`) that can be ran without the rest of the stack to test during development.

To run the local version, simply run"

```bash
pip install -r requirements.txt
python -m bytewax.run dataflow.pre:flow
```

## How it works

The dataflow will first load the products into memory in a `product_id:product_data` dictionary and then while listening to new orders it will flat map the list of items in the order and then enrich those items from the product data in the dictionary. 

If the products are constantly changing, this could be redesigned to make an initial request from the products database and if a product id is encountered that can't be found in the dictionary, the products could be pulled again.

### Generating Orders

in the `data/` directory you can find the `generate_orders.py` file that is used to generate the `orders.jsonl` file.
