import streamlit as st
import pandas as pd
import os

st.title("🛠️ Admin Dashboard - KaamWale")

st.subheader("📋 Registered Workers List")
csv_file = "worker_data.csv"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)

    if 'status' not in df.columns:
        df['status'] = 'pending'

    # Filter section
    filter_location = st.text_input("Filter by Location (optional)").strip()
    filter_job = st.selectbox("Filter by Job Type (optional)", ["", "Plumber", "Electrician", "Painter", "Driver", "Carpenter", "Other"])
    filter_status = st.selectbox("Filter by Status (optional)", ["", "pending", "verified", "rejected"])

    filtered_df = df.copy()

    if filter_location:
        filtered_df = filtered_df[filtered_df["Location"].str.contains(filter_location, case=False, na=False)]
    if filter_job:
        filtered_df = filtered_df[filtered_df["Job Type"] == filter_job]
    if filter_status:
        filtered_df = filtered_df[filtered_df["status"] == filter_status]

    st.dataframe(filtered_df)

    if filtered_df.empty:
        st.warning("⚠️ No worker data found. Please register some workers first.")
    else:
        for index, row in filtered_df.iterrows():
            with st.expander(f"{row['Name']} ({row['Job Type']})"):
                st.write(f"📍 Location: {row['Location']}")
                st.write(f"📞 Phone: {row['Phone']}")

                status = st.radio(
                    "Select Status",
                    ['pending', 'verified', 'rejected'],
                    index=['pending', 'verified', 'rejected'].index(row['status']),
                    key=f"status_{index}"
                )
                df.at[index, 'status'] = status

        if st.button("💾 Save Status Updates"):
            df.to_csv(csv_file, index=False)
            st.success("✅ Worker status updated successfully!")

else:
    st.warning("⚠️ No worker data found. Please register some workers first.")