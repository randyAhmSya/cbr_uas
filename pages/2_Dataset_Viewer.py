import streamlit as st
import pandas as pd

st.title("Dataset Viewer")
st.write("Menampilkan seluruh data transaksi kopi.")

df = pd.read_hdf("/data/coffee_sales.h5")
st.dataframe(df)
