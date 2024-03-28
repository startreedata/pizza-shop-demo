import streamlit as st
import pandas as pd
from pinotdb import connect
from datetime import datetime
import time
import plotly.graph_objects as go
import os

pinot_host = os.environ.get("PINOT_SERVER", "pinot-broker")
pinot_port = os.environ.get("PINOT_PORT", 8099)
conn = connect(pinot_host, pinot_port)

st.set_page_config(layout="wide")
st.title("All About That Dough Dashboard 🍕")

now = datetime.now()
dt_string = now.strftime("%B %-d, %Y at %-I:%M:%S %p")
st.info(f"**Last update:** {dt_string}", icon="ℹ️")

# Use session state to keep track of whether we need to auto refresh the page and the refresh frequency
if not "sleep_time" in st.session_state:
    st.session_state.sleep_time = 5

if not "auto_refresh" in st.session_state:
    st.session_state.auto_refresh = True

mapping2 = {
    "1 hour": {"period": "PT60M", "previousPeriod": "PT120M", "granularity": "minute"},
    "30 minutes": {"period": "PT30M", "previousPeriod": "PT60M", "granularity": "minute"},
    "10 minutes": {"period": "PT10M", "previousPeriod": "PT20M", "granularity": "second"},
    "5 minutes": {"period": "PT5M", "previousPeriod": "PT10M", "granularity": "second"},
    "1 minute": {"period": "PT1M", "previousPeriod": "PT2M", "granularity": "second"}
}

with st.expander("Dashboard settings", expanded=True):
    if st.session_state.auto_refresh:
        left, right = st.columns(2)

        with left:
            auto_refresh = st.toggle('Auto-refresh', value=st.session_state.auto_refresh)

            if auto_refresh:
                number = st.number_input('Refresh rate in seconds', value=st.session_state.sleep_time)
                st.session_state.sleep_time = number

        with right:
            time_ago = st.radio("Display data from the last", mapping2.keys(), horizontal=True, key="time_ago", index=len(mapping2.keys()) - 1)

curs = conn.cursor()

pinot_available = False
try:
    curs.execute("select * FROM orders where ts > ago('PT2M')")
    if not curs.description:
        st.warning("Connected to Pinot, but no orders imported", icon="⚠️")

    pinot_available = curs.description is not None
except Exception as e:
    st.warning(f"""Unable to connect to or query Apache Pinot [{pinot_host}:{pinot_port}] Exception: {e}""", icon="⚠️")

if pinot_available:
    query = """
    select count(*) FILTER(WHERE  ts > ago(%(nearTimeAgo)s)) AS events1Min,
           count(*) FILTER(WHERE  ts <= ago(%(nearTimeAgo)s) AND ts > ago(%(timeAgo)s)) AS events1Min2Min,
           sum("price") FILTER(WHERE  ts > ago(%(nearTimeAgo)s)) AS total1Min,
           sum("price") FILTER(WHERE  ts <= ago(%(nearTimeAgo)s) AND ts > ago(%(timeAgo)s)) AS total1Min2Min
    from orders
    where ts > ago(%(timeAgo)s)
    limit 1
    """

    curs.execute(query, {
        "timeAgo": mapping2[time_ago]["previousPeriod"],
        "nearTimeAgo": mapping2[time_ago]["period"]
    })

    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    metrics_container = st.container(border=True)
    metrics_container.subheader(f"Orders in the last {time_ago}")

    num_orders, rev, order_val = metrics_container.columns(3)
    num_orders.metric(
        label="Number of orders",
        value="{:,}".format(int(df['events1Min'].values[0])),
        delta="{:,}".format(int(df['events1Min'].values[0] - df['events1Min2Min'].values[0])) if df['events1Min2Min'].values[0] > 0 else None
    )

    rev.metric(
        label="Revenue in ₹",
        value="{:,.2f}".format(df['total1Min'].values[0]),
        delta="{:,.2f}".format(df['total1Min'].values[0] - df['total1Min2Min'].values[0]) if df['total1Min2Min'].values[0] > 0 else None
    )

    average_order_value_1min = df['total1Min'].values[0] / int(df['events1Min'].values[0])
    average_order_value_1min_2min = df['total1Min2Min'].values[0] / int(df['events1Min2Min'].values[0]) if int(df['events1Min2Min'].values[0]) > 0 else 0

    order_val.metric(
        label="Average order value in ₹",
        value="{:,.2f}".format(average_order_value_1min),
        delta="{:,.2f}".format(average_order_value_1min - average_order_value_1min_2min) if average_order_value_1min_2min > 0 else None
    )

    query = """
    select ToDateTime(DATETRUNC(%(granularity)s, ts), 'yyyy-MM-dd HH:mm:ss') AS dateMin, 
        count(*) AS orders, 
        sum(price) AS revenue
    from orders
    where ts > ago(%(timeAgo)s)
    group by dateMin
    order by dateMin desc
    LIMIT 10000
    """

    curs.execute(query, {"timeAgo": mapping2[time_ago]["period"], "granularity": mapping2[time_ago]["granularity"]})

    df_ts = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    if df_ts.shape[0] > 1:
        df_ts_melt = pd.melt(df_ts, id_vars=['dateMin'], value_vars=['revenue', 'orders'])

        col1, col2 = st.columns(2)
        with col1:
            orders = df_ts_melt[df_ts_melt.variable == "orders"]
            latest_date = orders.dateMin.max()
            latest_date_but_one = orders.sort_values(by=["dateMin"], ascending=False).iloc[[1]].dateMin.values[0]

            revenue_complete = orders[orders.dateMin < latest_date]
            revenue_incomplete = orders[orders.dateMin >= latest_date_but_one]

            fig = go.FigureWidget(data=[
                go.Scatter(x=revenue_complete.dateMin, y=revenue_complete.value, mode='lines', line={'dash': 'solid', 'color': 'green'}),
                go.Scatter(x=revenue_incomplete.dateMin, y=revenue_incomplete.value, mode='lines', line={'dash': 'dash', 'color': 'green'}),
            ])
            fig.update_layout(showlegend=False, title=f"Orders per {mapping2[time_ago]['granularity']}", margin=dict(l=0, r=0, t=40, b=0), )
            fig.update_yaxes(range=[0, df_ts["orders"].max() * 1.1])
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            revenue = df_ts_melt[df_ts_melt.variable == "revenue"]
            latest_date = revenue.dateMin.max()
            latest_date_but_one = revenue.sort_values(by=["dateMin"], ascending=False).iloc[[1]].dateMin.values[0]

            revenue_complete = revenue[revenue.dateMin < latest_date]
            revenue_incomplete = revenue[revenue.dateMin >= latest_date_but_one]

            fig = go.FigureWidget(data=[
                go.Scatter(x=revenue_complete.dateMin, y=revenue_complete.value, mode='lines', line={'dash': 'solid', 'color': 'blue'}),
                go.Scatter(x=revenue_incomplete.dateMin, y=revenue_incomplete.value, mode='lines', line={'dash': 'dash', 'color': 'blue'}),
            ])
            fig.update_layout(showlegend=False, title=f"Revenue per {mapping2[time_ago]['granularity']}", margin=dict(l=0, r=0, t=40, b=0), )
            fig.update_yaxes(range=[0, df_ts["revenue"].max() * 1.1])
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        curs.execute("""
        SELECT ToDateTime(ts, 'HH:mm:ss:SSS') AS dateTime, status, price, userId, productsOrdered, totalQuantity
        FROM orders
        ORDER BY ts DESC
        LIMIT 10
        """)

        df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
        # Potential todo: convert time to datetime for better formatting in data_editor
        with st.container(border=True):
            st.subheader("Latest orders")
            st.data_editor(
                df,
                column_config={
                    "dateTime": "Time",
                    "status": "Status",
                    "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                    "userId": st.column_config.NumberColumn("User ID", format="%d"),
                    "productsOrdered": st.column_config.NumberColumn("Quantity", help="Quantity of distinct products ordered", format="%d"),
                    "totalQuantity": st.column_config.NumberColumn("Total quantity", help="Total quantity ordered", format="%d"),
                },
                disabled=True
            )

    with right:
        with st.container(border=True):
            st.subheader("Most popular categories")

            curs.execute("""
            SELECT "product.category" AS category, 
                    distinctcount(orderId) AS orders,
                    sum("orderItem.quantity") AS quantity
            FROM order_items_enriched
            where ts > ago(%(timeAgo)s)
            group by category
            ORDER BY count(*) DESC
            LIMIT 5
            """, {"timeAgo": mapping2[time_ago]["period"]})

            df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
            df["quantityPerOrder"] = df["quantity"] / df["orders"]

            st.data_editor(
                df,
                column_config={
                    "category": "Category",
                    "orders": st.column_config.NumberColumn("Number of orders", format="%d"),
                    "quantity": st.column_config.NumberColumn("Total quantity ordered", format="$%d"),
                    "quantityPerOrder": st.column_config.NumberColumn("Average quantity per order", format="%d"),
                },
                disabled=True
            )

    curs.execute("""
    SELECT "product.name" AS product, 
            "product.image" AS image,
            distinctcount(orderId) AS orders,
            sum("orderItem.quantity") AS quantity
    FROM order_items_enriched
    where ts > ago(%(timeAgo)s)
    group by product, image
    ORDER BY count(*) DESC
    LIMIT 5
    """, {"timeAgo": mapping2[time_ago]["period"]})

    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    df["quantityPerOrder"] = df["quantity"] / df["orders"]

    with st.container(border=True):
        st.subheader("Most popular items")
        st.data_editor(
            df,
            use_container_width=True,
            column_config={
                "product": "Product",
                "image": st.column_config.ImageColumn(label="Image", width="medium"),
                "orders": st.column_config.NumberColumn("Number of orders", format="%d"),
                "quantity": st.column_config.NumberColumn("Total quantity ordered", format="$%d"),
                "quantityPerOrder": st.column_config.NumberColumn("Average quantity per order", format="%d"),
            },
            disabled=True
        )

    curs.close()

if auto_refresh:
    time.sleep(number)
    st.experimental_rerun()
