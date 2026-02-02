import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("global_sales.csv")
    df.columns = df.columns.str.strip().str.lower()
    df["invoicedate"] = pd.to_datetime(df["invoicedate"])
    df["sales"] = df["quantity"] * df["unitprice"]
    df = df[df["sales"] > 0]
    return df

df = load_data()

st.title("Global Sales Analytics Dashboard")
st.markdown("Interactive dashboard exploring global sales performance, customer behavior, and country-level insights.")

st.sidebar.header("Dashboard Filters")

countries = st.sidebar.multiselect(
    "Select Countries",
    sorted(df["country"].unique()),
    default=df["country"].unique()[:5]
)

years = st.sidebar.slider(
    "Select Year Range",
    int(df["invoicedate"].dt.year.min()),
    int(df["invoicedate"].dt.year.max()),
    (2010, 2011)
)

months = st.sidebar.multiselect(
    "Select Months",
    list(range(1, 13)),
    default=list(range(1, 13))
)

filtered_df = df[
    (df["country"].isin(countries)) &
    (df["invoicedate"].dt.year.between(years[0], years[1])) &
    (df["invoicedate"].dt.month.isin(months))
]

total_sales = filtered_df["sales"].sum()
total_customers = filtered_df["customerid"].nunique()
avg_order_value = filtered_df.groupby("invoiceno")["sales"].sum().mean()
total_orders = filtered_df["invoiceno"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("👥 Total Customers", f"{total_customers:,}")
col3.metric("🧾 Total Orders", f"{total_orders:,}")
col4.metric("📦 Avg Order Value", f"${avg_order_value:,.2f}")

st.divider()

sales_by_year = (
    filtered_df.groupby(filtered_df["invoicedate"].dt.year)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_sales_trend = px.line(
    sales_by_year,
    x="invoicedate",
    y="total_sales",
    markers=True,
    title="Global Sales Trend Over Time",
    labels={"invoicedate": "Year", "total_sales": "Total Sales"}
)

st.plotly_chart(fig_sales_trend, use_container_width=True)

st.divider()

country_sales = (
    filtered_df.groupby("country")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig_country_sales = px.bar(
    country_sales,
    x="sales",
    y="country",
    orientation="h",
    title="Top 10 Countries by Total Sales",
    labels={"sales": "Total Sales", "country": "Country"}
)

st.plotly_chart(fig_country_sales, use_container_width=True)

st.divider()

monthly_sales = (
    filtered_df.groupby(filtered_df["invoicedate"].dt.month)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_monthly = px.area(
    monthly_sales,
    x="invoicedate",
    y="total_sales",
    title="Seasonal Sales Pattern by Month",
    labels={"invoicedate": "Month", "total_sales": "Total Sales"}
)

st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

country_perf = (
    filtered_df.groupby("country")
    .agg(
        total_sales=("sales", "sum"),
        total_orders=("invoiceno", "nunique")
    )
    .reset_index()
    .sort_values("total_sales", ascending=False)
    .head(10)
)

fig_country_perf = px.bar(
    country_perf,
    x="total_sales",
    y="country",
    orientation="h",
    color="total_orders",
    color_continuous_scale="blues",
    title="Top Countries: Sales & Order Volume",
    labels={
        "total_sales": "Total Sales",
        "country": "Country",
        "total_orders": "Order Volume"
    }
)

st.plotly_chart(fig_country_perf, use_container_width=True)

st.divider()

aov_country = (
    filtered_df.groupby("country")
    .apply(lambda x: x.groupby("invoiceno")["sales"].sum().mean())
    .reset_index(name="avg_order_value")
    .sort_values("avg_order_value", ascending=False)
    .head(10)
)

fig_aov = px.bar(
    aov_country,
    x="avg_order_value",
    y="country",
    orientation="h",
    title="Top Countries by Average Order Value",
    labels={"avg_order_value": "Average Order Value", "country": "Country"}
)

st.plotly_chart(fig_aov, use_container_width=True)

st.divider()

st.subheader("Filtered Dataset Preview")
st.dataframe(filtered_df.head(100))
