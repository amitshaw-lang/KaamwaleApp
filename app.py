import streamlit as st
import pandas as pd

# App title
st.title("KaamWale App")

# Sidebar navigation
page = st.sidebar.radio("Navigate", [
    "Home", "Privacy Policy", "Customer Signup", "Worker Profile",
    "Admin Dashboard", "Customer Job Post", "Job Filter", "Test Read CSV", "Aadhaar Upload"
])

# Home page
if page == "Home":
    st.subheader("Welcome to KaamWale App!")
    st.write("Use the sidebar to navigate different features of the app.")

# Privacy Policy
elif page == "Privacy Policy":
    st.subheader("🔒 Privacy Policy")
    st.markdown("""
    We respect your privacy:
    - Your data is safe.
    - We do not share your info with third parties.
    - For any concerns, contact: support@kaamwaleapp.com
    """)

# Customer Signup
elif page == "Customer Signup":
    st.subheader("📝 Customer Signup")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    if st.button("Signup"):
        st.success(f"Customer {name} signed up with phone {phone}!")

# Worker Profile
elif page == "Worker Profile":
    st.subheader("👷 Worker Profile")
    st.info("Worker profile management coming soon.")

# Admin Dashboard
elif page == "Admin Dashboard":
    st.subheader("🛡️ Admin Dashboard")
    st.info("Admin dashboard features coming soon.")

# Customer Job Post
elif page == "Customer Job Post":
    st.subheader("📌 Post a Job")
    title = st.text_input("Job Title")
    location = st.text_input("Job Location")
    job_type = st.text_input("Job Type")
    if st.button("Post Job"):
        st.success(f"Job '{title}' posted at '{location}' for '{job_type}'.")

# Job Filter
elif page == "Job Filter":
    st.subheader("🔍 Job Filter")
    try:
        df = pd.read_csv('job_requests.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ job_requests.csv not found.")

# Test Read CSV
elif page == "Test Read CSV":
    st.subheader("📂 Test Read Worker CSV")
    try:
        df = pd.read_csv('worker_data.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ worker_data.csv not found.")

# Aadhaar Upload
elif page == "Aadhaar Upload":
    st.subheader("📑 Upload Aadhaar Card")
    uploaded_file = st.file_uploader("Choose Aadhaar file (PDF/Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.success("Aadhaar file uploaded successfully!")
        st.write("File details:")
        st.write(f"Name: {uploaded_file.name}")
        st.write(f"Type: {uploaded_file.type}")