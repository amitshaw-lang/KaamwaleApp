import streamlit as st
import pandas as pd

st.set_page_config(page_title="KaamWale App", layout="wide")

# Title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>KaamWale App 🚀</h1>", unsafe_allow_html=True)

# Session for login users
if "users" not in st.session_state:
    st.session_state["users"] = {}
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# Sidebar navigation
menu = st.sidebar.radio("📌 Navigate", [
    "Home",
    "Privacy Policy",
    "Customer Signup",
    "Customer Login",
    "Worker Profile",
    "Admin Dashboard",
    "Customer Job Post",
    "Job Filter",
    "Test Read CSV",
    "Payment",
    "Aadhar Upload",
    "GPS Location",
    "About"
])

# Home
if menu == "Home":
    st.subheader("🏠 Welcome to KaamWale App!")
    st.write("Use the sidebar to explore features. This app helps customers hire workers easily.")

# Privacy Policy
elif menu == "Privacy Policy":
    st.subheader("🔒 Privacy Policy")
    st.markdown("""
    - Your data is safe with us.
    - We do not share data with third parties.
    - Uploaded files (e.g. Aadhar) are handled securely in memory.
    - Contact: support@kaamwaleapp.com
    """)

# Customer Signup
elif menu == "Customer Signup":
    st.subheader("👤 Customer Signup")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    if st.button("Signup"):
        if username in st.session_state["users"]:
            st.error("❌ Username already exists!")
        else:
            st.session_state["users"][username] = password
            st.success("✅ Signup successful!")

# Customer Login
elif menu == "Customer Login":
    st.subheader("🔑 Customer Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state["users"] and st.session_state["users"][username] == password:
            st.session_state["logged_in_user"] = username
            st.success(f"✅ Welcome {username}!")
        else:
            st.error("❌ Invalid credentials")

# Worker Profile
elif menu == "Worker Profile":
    st.subheader("👷 Worker Profile")
    name = st.text_input("Worker Name")
    skill = st.text_input("Skill")
    if st.button("Save Worker"):
        st.success(f"Saved worker: {name}, skill: {skill}")

# Admin Dashboard
elif menu == "Admin Dashboard":
    st.subheader("🛠 Admin Dashboard")
    st.info("Admin tools will come here")

# Customer Job Post
elif menu == "Customer Job Post":
    st.subheader("📌 Post a Job")
    job = st.text_input("Job Title")
    loc = st.text_input("Job Location")
    if st.button("Post Job"):
        st.success(f"Posted job: {job} at {loc}")

# Job Filter
elif menu == "Job Filter":
    st.subheader("🔍 Job Filter")
    try:
        df = pd.read_csv('job_requests.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ job_requests.csv not found.")

# Test Read CSV
elif menu == "Test Read CSV":
    st.subheader("📄 Test Read worker_data.csv")
    try:
        df = pd.read_csv('worker_data.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("❌ worker_data.csv not found.")

# Payment
elif menu == "Payment":
    st.subheader("💳 Razorpay Payment")
    st.markdown("Click below to pay ₹100")
    rzp_url = "https://rzp.io/l/your-payment-link"  # Replace with real Razorpay link
    if st.button("Pay Now"):
        st.markdown(f"[👉 Click to pay ₹100]({rzp_url})", unsafe_allow_html=True)

# Aadhar Upload
elif menu == "Aadhar Upload":
    st.subheader("📂 Upload Aadhar Card (Secure)")
    file = st.file_uploader("Upload Aadhar (PDF/Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
    if file:
        st.success(f"{file.name} uploaded successfully (not saved on server).")

# GPS Location (Advanced UI)
elif menu == "GPS Location":
    st.subheader("📍 GPS Location")
    st.markdown("""
    <div id="geo-output">Click below and allow permission to get your location.</div>
    <button onclick="getLocation()">Get Location</button>
    <script>
    function getLocation() {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                document.getElementById('geo-output').innerText = 
                `Latitude: ${pos.coords.latitude}, Longitude: ${pos.coords.longitude}`;
            },
            (err) => {
                document.getElementById('geo-output').innerText = `Error: ${err.message}`;
            }
        );
    }
    </script>
    """, unsafe_allow_html=True)

# About
elif menu == "About":
    st.subheader("ℹ About App")
    st.write("""
    **KaamWale App** is designed to help customers hire workers easily.
    All features are for demo. Real data persistence, GPS secure API and payments need production setup.
    """)

# Footer
st.markdown("---")
st.markdown("<small>KaamWale App © 2025 | All rights reserved.</small>", unsafe_allow_html=True)