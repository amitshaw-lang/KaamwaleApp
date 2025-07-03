import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="KaamWale",
    page_icon="🛠",
    layout="centered"
)

st.title("👋 Welcome to KaamWale App")
st.subheader("Sab Kaam Ek App Se")

st.markdown("""
### 📌 Sidebar se page select karein:
- Customer Signup
- Worker Profile Upload
- Admin Dashboard (if added)
""")

# Sidebar button for Privacy Policy
if st.sidebar.button("📄 View Privacy Policy"):
    st.switch_page("PrivacyPolicy.py")  # agar tum streamlit-multipage use kar rahe ho
    # ya agar switch_page nahi hai to ek link dikha do
    # st.sidebar.markdown("[View Privacy Policy](PrivacyPolicy.py)")

# Main content
st.caption("Made in 🇮🇳 with ❤️ by Amit Kumar Shaw")

csv_file = 'worker_data.csv'
df = pd.read_csv(csv_file)

st.write(df.columns.tolist())  # Columns list dikhane ke liye
st.write(df)  # Full data dikhane ke liye

# Main page bottom Privacy Policy link
st.markdown("---")
st.markdown("📄 [View Privacy Policy](PrivacyPolicy.py)")