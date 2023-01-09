#!/bin/bash

./bin/pinot-admin.sh AddTable -schemaFile /config/orders/schema.json -tableConfigFile /config/orders/table.json -controllerHost pinot-controller -exec
status1=$?

if [ "$status1" = "255" ] || [ "$status1" = "0" ] 
then
    ./bin/pinot-admin.sh AddTable -schemaFile /config/order_items_enriched/schema.json -tableConfigFile /config/order_items_enriched/table.json -controllerHost pinot-controller -exec
    status2=$?

    if [ "$status2" = "255" ] || [ "$status2" = "0" ] 
    then
        exit 0
    else
        exit $status2
    fi
else
    exit $status1    
fi