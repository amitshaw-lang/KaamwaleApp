
import streamlit as st
import pandas as pd
import os

# 🔧 Worker detail input
name = st.text_input("Name")
phone = st.text_input("Mobile Number")
location = st.text_input("Location (Area)")
job_type = st.selectbox("Aap kya kaam karte hain?", ["Plumber", "Electrician", "Car repair", "Painter", "Bamboo House", "Agriculture"])
aadhaar = st.file_uploader("Aadhaar Card Upload (PDF or Image)", type=["jpg", "jpeg", "png", "pdf"])

# 🚀 Button logic
if st.button("Submit Profile"):
    if name and phone and location and job_type and aadhaar:
        st.success("Thank you, " + name + "! Aapka profile submit ho gaya.")

        # 💾 CSV mein data save karna
        data = {
            "Name": name,
            "Phone": phone,
            "Location": location,
            "Job Type": job_type,
            "Aadhaar": aadhaar.name
        }

        df = pd.DataFrame([data])
        csv_file = "worker_data.csv"

        if not os.path.exists(csv_file):
            df.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, mode='a', header=False, index=False)

        st.info("📁 Aapka data worker_data.csv file mein save ho gaya hai.")
    else:
        st.warning("⚠️ Kripya sabhi fields bharen.")