import streamlit as st
import pandas as pd

st.title("KaamWale App")

# Sidebar navigation
menu = st.sidebar.radio("Navigate", [
    "Home", 
    "Privacy Policy", 
    "Customer Signup", 
    "Worker Profile", 
    "Admin Dashboard", 
    "Customer Job Post", 
    "Job Filter", 
    "Test Read CSV", 
    "Payment",
    "Aadhar Upload",
    "GPS Location"
])

if menu == "Home":
    st.subheader("🏠 Welcome to KaamWale App!")
    st.write("Use the sidebar to explore features.")

elif menu == "Privacy Policy":
    st.subheader("🔒 Privacy Policy")
    st.markdown("""
    **KaamWale App Privacy Policy**
    
    - We respect your privacy and your data is safe with us.
    - No personal data is shared with third parties.
    - Aadhar and contact info are securely stored.
    - For queries: support@kaamwaleapp.com
    """)

elif menu == "Customer Signup":
    st.subheader("👤 Customer Signup")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    if st.button("Signup"):
        st.success(f"Customer {name} signed up successfully!")

elif menu == "Worker Profile":
    st.subheader("👷 Worker Profile")
    st.write("Worker profile management will go here.")

elif menu == "Admin Dashboard":
    st.subheader("🛠 Admin Dashboard")
    st.write("Admin functionalities will go here.")

elif menu == "Customer Job Post":
    st.subheader("📌 Post a Job")
    title = st.text_input("Job Title")
    location = st.text_input("Job Location")
    if st.button("Post Job"):
        st.success(f"Job '{title}' posted at '{location}'.")

elif menu == "Job Filter":
    st.subheader("🔍 Job Filter")
    try:
        df = pd.read_csv('job_requests.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("Job requests file not found.")

elif menu == "Test Read CSV":
    st.subheader("📄 Test Read CSV")
    try:
        df = pd.read_csv('worker_data.csv')
        st.dataframe(df)
    except FileNotFoundError:
        st.error("Worker data file not found.")

elif menu == "Payment":
    st.subheader("💳 Razorpay Payment")
    st.markdown("Click below to pay ₹100")
    razorpay_url = "https://rzp.io/l/your-payment-link"  # Replace with actual Razorpay link
    if st.button("Pay Now"):
        st.markdown(f"[Click here to pay]({razorpay_url})", unsafe_allow_html=True)

elif menu == "Aadhar Upload":
    st.subheader("📂 Upload Aadhar Card")
    uploaded_file = st.file_uploader("Upload your Aadhar (PDF/Image)")
    if uploaded_file:
        st.success(f"{uploaded_file.name} uploaded successfully.")

elif menu == "GPS Location":
    st.subheader("📍 GPS Location")
    st.markdown("""
    **Note:** Please allow location permission in your browser.
    """)
    st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const el = document.getElementById('geo-output');
            if (el) {
                el.innerText = `Latitude: ${lat}, Longitude: ${lon}`;
            }
        },
        (err) => {
            const el = document.getElementById('geo-output');
            if (el) {
                el.innerText = `Error: ${err.message}`;
            }
        }
    );
    </script>
    <div id="geo-output">Waiting for location...</div>
    """, unsafe_allow_html=True)