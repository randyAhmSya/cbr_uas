import streamlit as st
import pandas as pd
st.title("Dataset Viewer")
st.write("Menampilkan seluruh data transaksi kopi.")

df = pd.read_csv("../uam/data/Coffe_sales.csv")
st.dataframe(df)
