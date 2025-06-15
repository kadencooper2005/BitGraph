import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bitcoin Price vs Key Events", layout="wide")

st.title("Bitcoin Price with Highlighted Weekly Events")

# ---------- 1. Load & process with caching ----------
@st.cache_data
def load_and_prepare_data():
    # Load and parse date
    price_df = pd.read_csv("btc_oyv.csv", parse_dates=[0])
    event_df = pd.read_csv("bitcoin_news.csv", parse_dates=[0])

    price_df.rename(columns={price_df.columns[0]: "Date"}, inplace=True)
    event_df.rename(columns={event_df.columns[0]: "Date"}, inplace=True)

    # One event per week (Monday for example)
    event_df["Week"] = event_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    event_df = event_df.sort_values("Date").drop_duplicates(subset="Week", keep="first")

    # Merge closest BTC price to the event date
    merged = pd.merge_asof(
        event_df.sort_values("Date"),
        price_df.sort_values("Date"),
        on="Date",
        direction="backward"
    )

    return price_df, merged

price_df, events_df = load_and_prepare_data()

# ---------- 2. Create hover text for Plotly (no links) ----------
events_df["hover"] = events_df.apply(
    lambda row: f"{row['Date'].date()}: {row['headline']}" if pd.notnull(row['headline']) else "",
    axis=1
)

# ---------- 3. Plot ----------
fig = go.Figure()

# BTC price line
fig.add_trace(go.Scatter(
    x=price_df["Date"],
    y=price_df["Open Price"],
    mode="lines",
    name="BTC Price",
    line=dict(color="royalblue", width=2)
))

# Event markers (one per week)
fig.add_trace(go.Scatter(
    x=events_df["Date"],
    y=events_df["Open Price"],
    mode="markers",
    marker=dict(color="red", size=8),
    text=events_df["hover"],
    hoverinfo="text",
    name="Key Weekly Event"
))

# Layout
fig.update_layout(
    title="Bitcoin Price vs One Key Event per Week",
    xaxis_title="Date",
    yaxis_title="BTC Price (USD)",
    hovermode="closest",
    height=650,
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    xaxis=dict(rangeslider_visible=True),
)

st.plotly_chart(fig, use_container_width=True)

# ---------- 4. Event table with headlines + links ----------
with st.expander("View Full Event List with Links"):
    display_df = events_df[["Date", "headline", "link"]].copy()
    display_df["link"] = display_df["link"].apply(
        lambda x: f"[Read Article]({x})" if pd.notnull(x) else ""
    )
    st.markdown(display_df.to_markdown(index=False), unsafe_allow_html=True)
