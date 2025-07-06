import streamlit as st
import pandas as pd
from datetime import date

st.title("📝 Job Posting - Customer")

# CSV file path
csv_file = "job_requests.csv"

# Load or initialize DataFrame
try:
    df = pd.read_csv(csv_file)
except:
    df = pd.DataFrame(columns=["Work Type", "Location", "Date", "Time", "Details", "Phone"])

# Input form
with st.form("job_form"):
    work_type = st.selectbox("Kaam ka type", ["Plumber", "Electrician", "Painter", "Driver", "Carpenter", "Other"])
    location = st.text_input("Location").strip()
    date_of_work = st.date_input("Date", date.today())
    time = st.selectbox("Time", ["Morning", "Afternoon", "Evening"])
    details = st.text_area("Details (optional)").strip()
    phone = st.text_input("Mobile Number (optional)").strip()

    submit = st.form_submit_button("Submit Job")

if submit:
    new_data = pd.DataFrame(
        [[work_type, location, date_of_work, time, details, phone if phone else ""]],
        columns=["Work Type", "Location", "Date", "Time", "Details", "Phone"]
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(csv_file, index=False)
    st.success("✅ Job successfully posted!")