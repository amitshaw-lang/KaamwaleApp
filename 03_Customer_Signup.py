import streamlit as st
import pandas as pd
import os

# Page title
st.title("Customer Signup – RozgarWale")
st.subheader("Apna account banaye aur workers dhoondhein!")

# Inputs
name = st.text_input("Naam")
phone = st.text_input("Phone Number")
location = st.text_input("Location (Address ya Area)")

# Submit
if st.button("Signup"):
    if name and phone and location:
        st.success("✅ Aap signup ho chuke hain!")

        # Save data to CSV
        data = {"Name": name, "Phone": phone, "Location": location}
        df = pd.DataFrame([data])

        csv_file = "customer_data.csv"

        if not os.path.exists(csv_file):
            df.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, mode='a', header=False, index=False)

        st.info("📁 Aapka data local file mein safe kar diya gaya hai.")
    else:
        st.warning("⚠️ Kripya sabhi fields bharein.")
