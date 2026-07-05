import streamlit as st
import pandas as pd
import plotly.express as px

# Configure the dashboard page
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

st.title("Sales Analytics Dashboard")

# Read the sales dataset
df = pd.read_csv("sales.csv", encoding="latin1")

# Remove empty rows
df.dropna(inplace=True)

# Convert order date into datetime format
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

# Remove rows with invalid dates
df = df.dropna(subset=["Order Date"])

# Extract month name for monthly analysis
df["Month"] = df["Order Date"].dt.strftime("%B")

# Sidebar filters
st.sidebar.header("Filters")

region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["Region"].unique())
)

category = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(df["Category"].unique())
)

# Create a copy of the original dataset
filtered = df.copy()

# Filter by selected region
if region != "All":
    filtered = filtered[filtered["Region"] == region]

# Filter by selected category
if category != "All":
    filtered = filtered[filtered["Category"] == category]

# Calculate dashboard metrics
total_sales = filtered["Sales"].sum()
total_orders = filtered["Order ID"].nunique()
avg_sales = filtered["Sales"].mean()

# Find top-selling product
top_product = (
    filtered.groupby("Product Name")["Sales"]
    .sum()
    .idxmax()
)

# Find category with highest sales
top_category = (
    filtered.groupby("Category")["Sales"]
    .sum()
    .idxmax()
)

# Display KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Orders", total_orders)
c3.metric("Average Sale", f"${avg_sales:,.2f}")
c4.metric("Top Category", top_category)

st.divider()

# Show important business insights
st.subheader("Business Insights")

st.write(f"Top Selling Product: **{top_product}**")
st.write(f"Best Category: **{top_category}**")
st.write(f"Total Revenue: **${total_sales:,.2f}**")

# Top 10 products by sales
st.subheader("Top 10 Products")

top_products = (
    filtered.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    x=top_products.values,
    y=top_products.index,
    orientation="h",
    labels={"x": "Sales", "y": "Product"},
    title="Top Products"
)

st.plotly_chart(fig, use_container_width=True)

# Monthly sales analysis
st.subheader("Monthly Sales Trend")

monthly = (
    filtered.groupby("Month")["Sales"]
    .sum()
    .reset_index()
)

months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

monthly["Month"] = pd.Categorical(
    monthly["Month"],
    categories=months,
    ordered=True
)

monthly = monthly.sort_values("Month")

fig = px.line(
    monthly,
    x="Month",
    y="Sales",
    markers=True,
    title="Monthly Sales"
)

st.plotly_chart(fig, use_container_width=True)

# Category-wise sales
st.subheader("Sales by Category")

category_sales = (
    filtered.groupby("Category")["Sales"]
    .sum()
    .reset_index()
)

fig = px.pie(
    category_sales,
    names="Category",
    values="Sales",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

# Region-wise sales
st.subheader("Sales by Region")

region_sales = (
    filtered.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

fig = px.bar(
    region_sales,
    x="Region",
    y="Sales",
    color="Region"
)

st.plotly_chart(fig, use_container_width=True)

# Top 10 states based on sales
st.subheader("Top 10 States")

state_sales = (
    filtered.groupby("State")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    state_sales,
    x="State",
    y="Sales",
    color="Sales"
)

st.plotly_chart(fig, use_container_width=True)

# Display top customers
st.subheader("Top 10 Customers")

customers = (
    filtered.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(customers, use_container_width=True)

# Allow user to download filtered data
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv,
    "filtered_sales.csv",
    "text/csv"
)