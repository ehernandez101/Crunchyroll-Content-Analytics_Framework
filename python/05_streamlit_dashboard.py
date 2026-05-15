import pandas as pd 
import streamlit as st
import plotly.express as px

df = pd.read_csv("../data/crunchyroll_anime_dataset.csv")

st.set_page_config(
    page_title="Crunchyroll Content Analytics Framework",
    layout="wide"
)

st.markdown( 
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 45%, #020617 100%);
        color: #F8FAFC;
    }

    h1, h2, h3, p, label {
        color: #F8FAFC !important;
    }

    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #475569;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.35);
    }

    div[data-testid="stMetricLabel"] {
        color: #CBD5E1 !important;
        font-size: 15px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 34px;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🎌 Crunchyroll Content Analytics Framework")
st.write("Anime content analytics dashboard focused on engagement, retention, churn risk, and viewer journey performance.")

# Sidebar filters
st.sidebar.header("Filters")

title_filter = st.sidebar.multiselect(
    "Anime Title",
    options=sorted(df["anime_title"].unique()),
    default=sorted(df["anime_title"].unique())
)

region_filter = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

genre_filter = st.sidebar.multiselect(
    "Genre",
    options=sorted(df["genre"].unique()),
    default=sorted(df["genre"].unique())
)

filtered = df[
    (df["anime_title"].isin(title_filter)) &
    (df["region"].isin(region_filter)) &
    (df["genre"].isin(genre_filter))
]

# KPI Cards
total_users = filtered["user_id"].nunique()
avg_watch_minutes = filtered["watch_minutes"].mean()
retention_rate = filtered["retained"].mean()
high_churn_rate = (filtered["churn_risk"] == "High").mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", f"{total_users:,}")
col2.metric("Avg Watch Minutes", f"{avg_watch_minutes:.1f}")
col3.metric("Retention Rate", f"{retention_rate:.2%}")
col4.metric("High Churn Risk", f"{high_churn_rate:.2%}")

st.divider()

# Charts
c1, c2 = st.columns(2)

with c1:
    title_watch = (
        filtered.groupby("anime_title")["watch_minutes"]
        .mean()
        .reset_index()
        .sort_values("watch_minutes", ascending=False)
    )

    fig = px.bar(
        title_watch,
        x="anime_title",
        y="watch_minutes",
        title="Average Watch Minutes by Anime Title",
        color_discrete_sequence=["#F97316"]
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    genre_retention = (
        filtered.groupby("genre")["retained"]
        .mean()
        .reset_index()
        .sort_values("retained", ascending=False)
    )

    fig = px.bar(
        genre_retention,
        x="genre",
        y="retained",
        title="Retention Rate by Genre",
        color_discrete_sequence=["#22C55E"]
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    churn_distribution = (
        filtered["churn_risk"]
        .value_counts()
        .reset_index()
    )
    churn_distribution.columns = ["churn_risk", "users"]

    fig = px.pie(
        churn_distribution,
        names="churn_risk",
        values="users",
        title="Churn Risk Distribution"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    region_watch = (
        filtered.groupby("region")["watch_minutes"]
        .mean()
        .reset_index()
        .sort_values("watch_minutes", ascending=False)
    )

    fig = px.bar(
        region_watch,
        x="region",
        y="watch_minutes",
        title="Average Watch Minutes by Region",
        color_discrete_sequence=["#38BDF8"]
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Executive Summary")
st.write(
    """
    This dashboard simulates how a content analytics team could evaluate anime title performance,
    viewer engagement, retention behavior, and churn risk. The framework supports decision-making
    across content strategy, programming, localization, and presentation surfaces.
    """
)
