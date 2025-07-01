import streamlit as st

st.set_page_config(
    page_title="KaamWale", 
    page_icon="🛠️", 
    layout="centered"
)

st.title("👋 Welcome to KaamWale App")
st.subheader("Sab Kaam Ek App Se")

st.markdown("""
### 👈 Sidebar se page select karein:

- Customer Signup
- Worker Profile Upload
- Admin Dashboard (if added)
""")

st.caption("Made in 🇮🇳 with ❤️ by Amit Kumar Shaw")
import pandas as pd

csv_file = 'worker_data.csv'
df = pd.read_csv(csv_file)

st.write(df.columns.tolist())  # Columns list dikhane ke liye
st.write(df)                   # Full data dikhane ke liye