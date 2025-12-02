import streamlit as st
import pandas as pd
import numpy as np

st.title("Sistem Rekomendasi Kopi Menggunakan CBR")

# Load dataset
df = pd.read_hdf("../uam/data/Coffe_sales.h5")


# ============================================================
# CLASS CBR DENGAN KOMENTAR LENGKAP
# ============================================================
class CBRCoffee:

    def __init__(self, dataset):
        self.df = dataset

        # ====== ENCODING KATEGORI (PREPROCESSING) ======
        self.time_map = {"Morning": 1, "Afternoon": 2, "Night": 3}
        self.weekday_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4,
                            "Fri": 5, "Sat": 6, "Sun": 7}
        self.month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                          "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                          "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

        # Apply encoding
        self.df["Time_num"] = self.df["Time_of_Day"].map(self.time_map)
        self.df["Weekday_num"] = self.df["Weekday"].map(self.weekday_map)
        self.df["Month_num"] = self.df["Month_name"].map(self.month_map)

        # Normalisasi numerik
        self.df["hour_norm"] = (
            self.df["hour_of_day"] - self.df["hour_of_day"].min()
        ) / (self.df["hour_of_day"].max() - self.df["hour_of_day"].min())

        self.df["money_norm"] = (
            self.df["money"] - self.df["money"].min()
        ) / (self.df["money"].max() - self.df["money"].min())

        # Bobot penilaian similarity
        self.weights = {
            "Time": 0.25,
            "Hour": 0.20,
            "Money": 0.25,
            "Weekday": 0.15,
            "Month": 0.15
        }

    # ========================================================
    # SIMILARITY FUNCTION
    # ========================================================
    
    # Numeric similarity
    def sim_numeric(self, a, b):
        """
        Similarity numerik menggunakan distance reduction:
        Semakin kecil selisih → semakin mirip.
        """
        return 1 - abs(a - b)

    # Categorical similarity
    def sim_cat(self, a, b):
        """
        Similarity kategori:
        Sama = 1, tidak sama = 0.
        """
        return 1 if a == b else 0

    # ========================================================
    # RETRIEVE — Mencari kasus lama yang paling mirip
    # ========================================================
    def compute_similarity(self, new, old):
        """
        Hitung similarity total terhadap satu kasus lama.
        """
        sim_time = self.sim_cat(new["Time"], old["Time_num"])
        sim_hour = self.sim_numeric(new["Hour"], old["hour_norm"])
        sim_money = self.sim_numeric(new["Money"], old["money_norm"])
        sim_weekday = self.sim_cat(new["Weekday"], old["Weekday_num"])
        sim_month = self.sim_cat(new["Month"], old["Month_num"])

        total_similarity = (
            sim_time * self.weights["Time"]
            + sim_hour * self.weights["Hour"]
            + sim_money * self.weights["Money"]
            + sim_weekday * self.weights["Weekday"]
            + sim_month * self.weights["Month"]
        )

        return total_similarity

    def retrieve(self, new_case):
        """
        RETRIEVE = mencari kasus paling mirip (similarity tertinggi)
        """
        similarities = []

        for idx, row in self.df.iterrows():
            sim = self.compute_similarity(new_case, row)
            similarities.append((idx, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)

        best_idx, best_sim = similarities[0]
        best_case = self.df.iloc[best_idx]

        return best_case, best_sim

    # ========================================================
    # REUSE — Mengambil solusi dari kasus paling mirip
    # ========================================================
    def reuse(self, best_case):
        """
        Ambil solusi langsung dari kasus lama → jenis kopi.
        """
        return best_case["coffee_name"]

    # ========================================================
    # REVISE — (Opsional) Koreksi solusi jika diperlukan
    # ========================================================
    def revise(self, recommendation):
        """
        Dalam implementasi ini, REVISE tidak dilakukan
        (solusi langsung dipakai dari kasus lama).
        """
        return recommendation  # tanpa revisi

    # ========================================================
    # RETAIN — Menyimpan kasus baru ke database kasus
    # ========================================================
    def retain(self, new_case, coffee_name):
        """
        Menyimpan kasus baru ke dataset bila ingin memperbarui knowledge.
        (Opsional)
        """
        new_row = {
            "Time_of_Day": new_case["Time"],
            "hour_of_day": new_case["Hour"],
            "money": new_case["Money"],
            "Weekday": new_case["Weekday"],
            "Month_name": new_case["Month"],
            "coffee_name": coffee_name,
        }

        self.df = self.df.append(new_row, ignore_index=True)
        self.df.to_csv("data/updated_cases.csv", index=False)

    # ========================================================
    # RECOMMEND (Main CBR Pipeline)
    # ========================================================
    def recommend(self, time, hour, money, weekday, month):

        # Encode new case
        new_case = {
            "Time": self.time_map[time],
            "Hour": (hour - self.df["hour_of_day"].min()) /
                    (self.df["hour_of_day"].max() - self.df["hour_of_day"].min()),
            "Money": (money - self.df["money"].min()) /
                     (self.df["money"].max() - self.df["money"].min()),
            "Weekday": self.weekday_map[weekday],
            "Month": self.month_map[month]
        }

        # Tahap 1: RETRIEVE
        best_case, sim = self.retrieve(new_case)

        # Tahap 2: REUSE
        recommendation = self.reuse(best_case)

        # Tahap 3: REVISE (tidak dilakukan)
        final_solution = self.revise(recommendation)

        # Tahap 4: RETAIN (opsional)
        # self.retain(new_case, final_solution)

        return final_solution, sim, best_case, new_case


# ============================================================
# STREAMLIT UI
# ============================================================
st.header("Input Kasus Baru")

# Form Input
with st.form("cbr_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time = st.selectbox("Time of Day", ["Morning", "Afternoon", "Night"])
        weekday = st.selectbox("Weekday", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])

    with col2:
        hour = st.number_input("Hour (0-23)", 0, 23, 10)
        month = st.selectbox("Month", list(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]))

    with col3:
        money = st.number_input("Money Spent", 1, 100, 25)

    submit = st.form_submit_button("Proses CBR")

if submit:
    cbr = CBRCoffee(df)
    result, sim, best_case, new_case = cbr.recommend(time, hour, money, weekday, month)

    st.success(f"Rekomendasi Kopi: **{result}** (Similarity: {sim:.4f})")

    st.subheader("Kasus Baru (Encoded)")
    st.json(new_case)

    st.subheader("Kasus Paling Mirip")
    st.dataframe(best_case)
