
import io
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Retail Repair Dashboard", layout="wide")

st.title("Retail Repair Dashboard")

st.markdown(
    """
    Upload today's Excel sheet (.xlsx) with columns **Merke** (brand) and **Tekniker** (technician).
    The app will automatically compute totals, show charts, and highlight today's **Top Technician**.
    """
)

uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("👆 Upload your Excel file to see the dashboard.")
    st.stop()

# Read Excel
try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Could not read the Excel file: {e}")
    st.stop()

# Normalize and validate columns
col_brand_candidates = ["Merke", "Product brand", "Brand"]
col_tech_candidates = ["Tekniker", "Service technician", "Technician"]

brand_col = next((c for c in col_brand_candidates if c in df.columns), None)
tech_col = next((c for c in col_tech_candidates if c in df.columns), None)

if brand_col is None or tech_col is None:
    st.error(
        f"Missing required columns. Found columns: {list(df.columns)}\n\n"
        f"Expected one of {col_brand_candidates} for brand and one of {col_tech_candidates} for technician."
    )
    st.stop()

# Trim whitespace and drop empty rows
df[brand_col] = df[brand_col].astype(str).str.strip()
df[tech_col] = df[tech_col].astype(str).str.strip()
df = df[(df[brand_col] != "") & (df[tech_col] != "")]

# KPIs
total_repairs = len(df)
unique_brands = df[brand_col].nunique()
repairs_per_technician = df[tech_col].value_counts().reset_index()
repairs_per_technician.columns = ["Technician", "Repairs"]
top_technician_row = repairs_per_technician.iloc[0] if not repairs_per_technician.empty else pd.Series({"Technician":"-", "Repairs":0})

# KPI cards
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Repairs", f"{total_repairs}")
kpi2.metric("Brands", f"{unique_brands}")
kpi3.metric("Top Technician", f"{top_technician_row['Technician']}", f"{int(top_technician_row['Repairs'])} repairs")

# Aggregations
repairs_per_brand = df[brand_col].value_counts().reset_index()
repairs_per_brand.columns = ["Brand", "Repairs"]

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Repairs by Brand")
    fig_brand = px.bar(
        repairs_per_brand,
        x="Brand",
        y="Repairs",
        text="Repairs"
    )
    fig_brand.update_traces(textposition="outside")
    fig_brand.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_brand, use_container_width=True)

with right:
    st.subheader("Repairs by Technician")
    # Donut chart
    if not repairs_per_technician.empty:
        fig_tech = px.pie(
            repairs_per_technician,
            names="Technician",
            values="Repairs",
            hole=0.5
        )
        fig_tech.update_layout(showlegend=True, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_tech, use_container_width=True)
    else:
        st.info("No technician data available.")

# Tables (optional)
with st.expander("Show tables"):
    c1, c2 = st.columns(2)
    with c1:
        st.write("Repairs per Brand")
        st.dataframe(repairs_per_brand, use_container_width=True)
    with c2:
        st.write("Repairs per Technician")
        st.dataframe(repairs_per_technician, use_container_width=True)
