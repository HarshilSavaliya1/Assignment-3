import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

st.title("Sales Analytics Dashboard")

cols = df.columns.tolist()

date_col = st.selectbox("Select Date Column", cols)
country_col = st.selectbox("Select Country Column", cols)
quantity_col = st.selectbox("Select Quantity Column", cols)
price_col = st.selectbox("Select Unit Price Column", cols)
customer_col = st.selectbox("Select Customer ID Column", cols)
invoice_col = st.selectbox("Select Invoice No Column", cols)

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

df = df.dropna(subset=[date_col, quantity_col, price_col])
df["sales"] = df[quantity_col] * df[price_col]

st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Countries",
    sorted(df[country_col].unique()),
    default=sorted(df[country_col].unique())[:5]
)

years = st.sidebar.slider(
    "Year Range",
    int(df[date_col].dt.year.min()),
    int(df[date_col].dt.year.max()),
    (
        int(df[date_col].dt.year.min()),
        int(df[date_col].dt.year.max())
    )
)

filtered_df = df[
    (df[country_col].isin(countries)) &
    (df[date_col].dt.year.between(years[0], years[1]))
]

total_sales = filtered_df["sales"].sum()
total_customers = filtered_df[customer_col].nunique()
total_orders = filtered_df[invoice_col].nunique()
avg_order_value = (
    filtered_df.groupby(invoice_col)["sales"].sum().mean()
    if total_orders > 0 else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{total_sales:,.2f}")
c2.metric("Customers", total_customers)
c3.metric("Orders", total_orders)
c4.metric("Avg Order Value", f"{avg_order_value:,.2f}")

sales_trend = (
    filtered_df.groupby(filtered_df[date_col].dt.year)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig1 = px.line(
    sales_trend,
    x=date_col,
    y="total_sales",
    markers=True,
    title="Sales Trend"
)
st.plotly_chart(fig1, use_container_width=True)

country_sales = (
    filtered_df.groupby(country_col)["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig2 = px.bar(
    country_sales,
    x="sales",
    y=country_col,
    orientation="h",
    title="Top Countries by Sales"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Data Preview")
st.dataframe(filtered_df.head(100))
