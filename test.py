import os
from random import random
import sys
import streamlit as st

x = 1
print("hello")

# write a python program to add two numbers
a = 5
b = 10
c = a + b
print(c + x + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10)  # Output: 15 + 55 = 70

# create a login page using streamlit and add a feature to check loyalty points

st.title("Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "user" and password == "pass":
        st.success("Login successful!")
    else:
        st.error("Invalid credentials")

st.header("🏅 RozgarWale Loyalty Points")
user_id = st.text_input("Enter Your ID")
if st.button("Check Points"):
    points = random.randint(50, 500)  # Generate random points
    st.success(f"You have {points} RozgarWale credits!")

    # create a worker profile page with image upload and rating system
    st.header("👷 Worker Profile")
    with st.form("worker_form"):
        name = st.text_input("Name")
        skill = st.selectbox(
            "Skill", ["Plumber", "Electrician", "Carpenter", "Mechanic"]
        )
        location = st.text_input("Location")
        phone = st.text_input("Phone")
        experience = st.text_input("Experience")
        aadhar = st.file_uploader("Upload Aadhaar")
        aadhar = None
        submit = st.form_submit_button("Submit")
    if submit:
        # --- 1) inputs clean/normalize ---
        nm = (name or "").strip()
        sk = (skill or "").strip()
        loc = (location or "").strip()
        ph = (phone or "").strip().replace(" ", "").replace("-", "")
        exp = (experience or "").strip()
        # --- 2) inputs validate ---
        if not nm:
            st.error("Name is required.")
        if not sk:
            st.error("Skill is required.")
        if not loc:
            st.error("Location is required.")
        if not ph:
            st.error("Phone is required.")
        if not exp:
            st.error("Experience is required.")
        if not aadhar:
            st.error("Aadhaar is required.")
