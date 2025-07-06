import streamlit as st
import pandas as pd

# App Title
st.set_page_config(page_title="KaamWale App", layout="wide")
st.title("💼 KaamWale App - Worker Data Viewer")

# Sidebar navigation
page = st.sidebar.radio(
    "📌 Navigate",
    ["Home", "Privacy Policy", "Customer Signup", "Worker Profile", "Admin Dashboard",
     "Customer Job Post", "Job Filter", "Test Read CSV"]
)

# Home page
if page == "Home":
    st.subheader("🏠 Welcome to KaamWale App!")
    st.write("Use the sidebar to navigate different features.")
    st.markdown("---")

# Privacy Policy
elif page == "Privacy Policy":
    st.subheader("🔒 Privacy Policy")
    st.markdown("""
    - Your data is safe.
    - We do not share your info with third parties.
    - All data stays local unless you explicitly share it.
    - For any concerns: [support@kaamwaleapp.com](mailto:support@kaamwaleapp.com)
    """)
    st.markdown("---")

# Customer Signup
elif page == "Customer Signup":
    st.subheader("📝 Customer Signup")
    name = st.text_input("Enter your Name")
    phone = st.text_input("Enter your Phone Number")
    if st.button("Signup"):
        if name and phone:
            st.success(f"✅ Customer {name} signed up with phone {phone}!")
        else:
            st.warning("Please fill both Name and Phone fields.")
    st.markdown("---")

# Worker Profile
elif page == "Worker Profile":
    st.subheader("👷 Worker Profile")
    st.write("Worker profile features coming soon...")
    st.markdown("---")

# Admin Dashboard
elif page == "Admin Dashboard":
    st.subheader("🛡️ Admin Dashboard")
    st.write("Admin features coming soon...")
    st.markdown("---")

# Customer Job Post
elif page == "Customer Job Post":
    st.subheader("📌 Post a Job")
    job_title = st.text_input("Job Title")
    location = st.text_input("Location")
    if st.button("Post Job"):
        if job_title and location:
            st.success(f"✅ Job '{job_title}' posted for location '{location}'!")
        else:
            st.warning("Please fill both Job Title and Location.")
    st.markdown("---")

# Job Filter
elif page == "Job Filter":
    st.subheader("🔍 Job Filter")
    try:
        df = pd.read_csv('job_requests.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ job_requests.csv file not found. Please check the file location.")
    st.markdown("---")

# Test Read CSV
elif page == "Test Read CSV":
    st.subheader("📄 Test Read CSV")
    try:
        df = pd.read_csv('worker_data.csv')
        st.success("✅ CSV file loaded successfully!")
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ worker_data.csv file not found. Please check the file location.")
    st.markdown("---")