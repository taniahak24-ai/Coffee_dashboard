import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Afficionado Coffee Roasters", layout="wide")

st.title("☕ Afficionado Coffee Roasters Dashboard")
st.write("Product Optimization & Revenue Contribution Analysis")

# ---------- Step 1: Find and read the data file ----------
# Put your data file in the same folder as this app.py
files = [f for f in os.listdir(".") if f.lower().endswith((".csv", ".xlsx", ".xls"))]

if len(files) == 0:
    st.error("No data file found. Please upload your Excel or CSV file to GitHub next to app.py")
    st.stop()

FILE_NAME = files[0]

@st.cache_data
def load_data(name):
    if name.lower().endswith(".csv"):
        data = pd.read_csv(name)
    else:
        data = pd.read_excel(name)
    # make column names simple: small letters, no spaces
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
    return data

df = load_data(FILE_NAME)

# ---------- Step 2: Check the columns ----------
needed = ["transaction_qty", "unit_price", "product_category", "product_type"]
missing = [c for c in needed if c not in df.columns]

if missing:
    st.error("These columns are not in your file: " + ", ".join(missing))
    st.write("Your file has these columns:")
    st.write(list(df.columns))
    st.stop()

# ---------- Step 3: Make the Revenue column ----------
df["revenue"] = df["transaction_qty"] * df["unit_price"]

# ---------- Step 4: Filters on the left side ----------
st.sidebar.header("Filters")

if "store_location" in df.columns:
    stores = st.sidebar.multiselect(
        "Store Location",
        df["store_location"].unique(),
        default=df["store_location"].unique(),
    )
    df = df[df["store_location"].isin(stores)]

cats = st.sidebar.multiselect(
    "Product Category",
    df["product_category"].unique(),
    default=df["product_category"].unique(),
)
df = df[df["product_category"].isin(cats)]

# ---------- Step 5: Big numbers ----------
c1, c2, c3 = st.columns(3)
c1.metric("Total Revenue", f"${df['revenue'].sum():,.0f}")
c2.metric("Total Items Sold", f"{df['transaction_qty'].sum():,.0f}")
c3.metric("Total Orders", f"{len(df):,}")

st.divider()

# ---------- Step 6: Charts ----------
left, right = st.columns(2)

cat_rev = df.groupby("product_category")["revenue"].sum().sort_values(ascending=False)

with left:
    st.subheader("Revenue by Product Category")
    st.bar_chart(cat_rev)

with right:
    st.subheader("Top 10 Products by Revenue")
    top10 = df.groupby("product_type")["revenue"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top10)

st.subheader("Revenue Contribution (%) by Product Category")
contrib = (cat_rev / cat_rev.sum() * 100).round(2)
st.dataframe(contrib.rename("Contribution %"))

if "transaction_date" in df.columns:
    st.subheader("Revenue Over Time")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    st.line_chart(df.groupby("transaction_date")["revenue"].sum())

# ---------- Step 7: Show some data ----------
st.subheader("Data Preview")
st.dataframe(df.head(100))
