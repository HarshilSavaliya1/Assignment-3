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

date_col = st.selectbox("Date column", cols)
country_col = st.selectbox("Country column", cols)
quantity_col = st.selectbox("Quantity column", cols)
price_col = st.selectbox("Unit price column", cols)
customer_col = st.selectbox("Customer ID column", cols)
invoice_col = st.selectbox("Invoice number column", cols)

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

df = df.dropna(subset=[date_col, quantity_col, price_col])

if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
    st.error("Selected date column is not datetime-compatible")
    st.stop()

df["sales"] = df[quantity_col] * df[price_col]

years = df[date_col].dt.year.dropna().unique()

if len(years) < 2:
    st.error("Not enough valid year values")
    st.stop()

min_year = int(years.min())
max_year = int(years.max())

countries = st.sidebar.multiselect(
    "Countries",
    sorted(df[country_col].dropna().unique()),
    default=sorted(df[country_col].dropna().unique())[:5]
)

year_range = st.sidebar.slider(
    "Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

filtered_df = df[
    (df[country_col].isin(countries)) &
    (df[date_col].dt.year.between(year_range[0], year_range[1]))
]

total_sales = filtered_df["sales"].sum()
total_customers = filtered_df[customer_col].nunique()
total_orders = filtered_df[invoice_col].nunique()
avg_order_value = filtered_df.groupby(invoice_col)["sales"].sum().mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{total_sales:,.2f}")
c2.metric("Customers", total_customers)
c3.metric("Orders", total_orders)
c4.metric("Avg Order Value", f"{avg_order_value:,.2f}")

trend = (
    filtered_df.groupby(filtered_df[date_col].dt.year)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig1 = px.line(trend, x=date_col, y="total_sales", markers=True)
st.plotly_chart(fig1, use_container_width=True)

top_countries = (
    filtered_df.groupby(country_col)["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig2 = px.bar(top_countries, x="sales", y=country_col, orientation="h")
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(filtered_df.head(100))
