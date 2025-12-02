import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Kopi",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Dashboard Data Penjualan Kopi")
st.write("Analitik transaksi kopi berdasarkan dataset historis.")

# Load Dataset
try:
    df = pd.read_csv("../uam/data/Coffe_sales.csv")
except:
    st.error("Dataset tidak ditemukan. Pastikan file berada di folder data/coffee_sales.csv")
    st.stop()

# ========================== Statistik ==========================
st.header("Statistik Utama")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transaksi", len(df))
col2.metric("Total Pendapatan", f"${df['money'].sum():.2f}")
col3.metric("Rata-rata Pembelian", f"${df['money'].mean():.2f}")
col4.metric("Jenis Kopi Unik", df["coffee_name"].nunique())

# ======================= Visualisasi ============================
st.header("Visualisasi Data")

st.subheader("Kopi Paling Banyak Dibeli")
st.bar_chart(df["coffee_name"].value_counts())

st.subheader("Total Pembelian per Jam")
hour = df.groupby("hour_of_day")["money"].sum()
st.line_chart(hour)

st.subheader("Pendapatan per Hari")
weekday = df.groupby("Weekday")["money"].sum()
st.bar_chart(weekday)

st.info("Gunakan sidebar untuk mengakses Sistem CBR dan Dataset Viewer.")
