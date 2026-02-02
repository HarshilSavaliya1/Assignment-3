import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Global Sales Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Load data (cached)
# --------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("train.csv")
    except FileNotFoundError:
        st.error("❌ Data file not found. Make sure 'train.csv' is in the GitHub repo root.")
        st.stop()

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Required columns check
    required_cols = {
        "country",
        "invoicedate",
        "quantity",
        "unitprice",
        "customerid",
        "invoiceno"
    }

    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
        st.stop()

    # Data cleaning
    df["invoicedate"] = pd.to_datetime(df["invoicedate"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unitprice"] = pd.to_numeric(df["unitprice"], errors="coerce")

    df = df.dropna(subset=["invoicedate", "quantity", "unitprice"])
    df["sales"] = df["quantity"] * df["unitprice"]
    df = df[df["sales"] > 0]

    return df


df = load_data()

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🌍 Global Sales Analytics Dashboard")
st.markdown(
    "Interactive dashboard exploring global sales performance, customer behavior, and country-level insights."
)

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Dashboard Filters")

countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())[:5]
)

years = st.sidebar.slider(
    "Select Year Range",
    int(df["invoicedate"].dt.year.min()),
    int(df["invoicedate"].dt.year.max()),
    (
        int(df["invoicedate"].dt.year.min()),
        int(df["invoicedate"].dt.year.max())
    )
)

months = st.sidebar.multiselect(
    "Select Months",
    options=list(range(1, 13)),
    default=list(range(1, 13))
)

# --------------------------------------------------
# Filter data
# --------------------------------------------------
filtered_df = df[
    (df["country"].isin(countries)) &
    (df["invoicedate"].dt.year.between(years[0], years[1])) &
    (df["invoicedate"].dt.month.isin(months))
]

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
total_sales = filtered_df["sales"].sum()
total_customers = filtered_df["customerid"].nunique()
total_orders = filtered_df["invoiceno"].nunique()
avg_order_value = (
    filtered_df.groupby("invoiceno")["sales"].sum().mean()
    if total_orders > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("👥 Customers", f"{total_customers:,}")
col3.metric("🧾 Orders", f"{total_orders:,}")
col4.metric("📦 Avg Order Value", f"${avg_order_value:,.2f}")

st.divider()

# --------------------------------------------------
# Sales trend by year
# --------------------------------------------------
sales_by_year = (
    filtered_df
    .groupby(filtered_df["invoicedate"].dt.year)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_trend = px.line(
    sales_by_year,
    x="invoicedate",
    y="total_sales",
    markers=True,
    title="Sales Trend Over Time",
    labels={"invoicedate": "Year", "total_sales": "Total Sales"}
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# --------------------------------------------------
# Top countries by sales
# --------------------------------------------------
country_sales = (
    filtered_df.groupby("country")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig_country = px.bar(
    country_sales,
    x="sales",
    y="country",
    orientation="h",
    title="Top 10 Countries by Total Sales",
    labels={"sales": "Total Sales", "country": "Country"}
)
st.plotly_chart(fig_country, use_container_width=True)

st.divider()

# --------------------------------------------------
# Monthly seasonality
# --------------------------------------------------
monthly_sales = (
    filtered_df.groupby(filtered_df["invoicedate"].dt.month)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_monthly = px.area(
    monthly_sales,
    x="invoicedate",
    y="total_sales",
    title="Monthly Sales Pattern",
    labels={"invoicedate": "Month", "total_sales": "Total Sales"}
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

# --------------------------------------------------
# Average order value by country
# --------------------------------------------------
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

# --------------------------------------------------
# Data preview
# --------------------------------------------------
st.subheader("Filtered Dataset Preview")
st.dataframe(filtered_df.head(100))
