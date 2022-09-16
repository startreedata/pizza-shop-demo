import pandas as pd
import streamlit as st
from pinotdb import connect

import plotly.graph_objects as go
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.header("Pizza App Dashboard ")

now = datetime.now()
dt_string = now.strftime("%d %B %Y %H:%M:%S")
st.write(f"Last update: {dt_string}")

if not "sleep_time" in st.session_state:
    st.session_state.sleep_time = 2 # <1>

if not "auto_refresh" in st.session_state:
    st.session_state.auto_refresh = True # <2>

auto_refresh = st.checkbox('Auto Refresh?', st.session_state.auto_refresh)

if auto_refresh:
    number = st.number_input('Refresh rate in seconds', value=st.session_state.sleep_time) # <3>
    st.session_state.sleep_time = number

conn = connect(host='localhost', port=9000, path='/sql', scheme='http')

query = """
    select count(*) FILTER(WHERE  ts > ago('PT1M')) AS events1Min,
        count(*) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS events1Min2Min,
        sum(total) FILTER(WHERE  ts > ago('PT1M')) AS total1Min,
        sum(total) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS total1Min2Min
    from orders 
    where ts > ago('PT2M')
    limit 1
"""
curs = conn.cursor()
curs.execute(query)
df_summary = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
# st.write(df_summary)

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    label="# of Orders",
    value="{:,}".format(int(df_summary['events1Min'].values[0])),
    delta="{:,}".format(int(df_summary['events1Min'].values[0] - df_summary['events1Min2Min'].values[0])) 
)

metric2.metric(
    label="Revenue in ₹",
    value="{:,.2f}".format(df_summary['total1Min'].values[0]),
    delta="{:,.2f}".format(df_summary['total1Min'].values[0] - df_summary['total1Min2Min'].values[0])
)

average_order_value_1min = df_summary['total1Min'].values[0] / int(df_summary['events1Min'].values[0])
average_order_value_1min_2min = df_summary['total1Min2Min'].values[0] / int(df_summary['events1Min2Min'].values[0])

metric3.metric(
    label="Average order value in ₹",
    value="{:,.2f}".format(average_order_value_1min),
    delta="{:,.2f}".format(average_order_value_1min - average_order_value_1min_2min) 
)

query = """
    select ToDateTime(DATETRUNC('minute', ts), 'yyyy-MM-dd hh:mm:ss') AS dateMin, 
        count(*) AS orders, 
        sum(total) AS revenue
    from orders 
    where ts > ago('PT1H')
    group by dateMin
    order by dateMin desc
    LIMIT 10000
    """

curs.execute(query)

df_ts = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

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
    fig.update_layout(showlegend=False, title="Orders per minute", margin=dict(l=0, r=0, t=40, b=0),)
    fig.update_yaxes(range=[0, df_ts["orders"].max() * 1.1])
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
    fig.update_layout(showlegend=False, title="Revenue per minute", margin=dict(l=0, r=0, t=40, b=0),)
    fig.update_yaxes(range=[0, df_ts["revenue"].max() * 1.1])
    st.plotly_chart(fig, use_container_width=True) 

if auto_refresh:
    time.sleep(number)
    st.experimental_rerun()    