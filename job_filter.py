import pandas as pd
import streamlit as st

def load_job_data():
    return pd.read_csv('job_requests.csv')

def main():
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>RozgarWale Job Filter System</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    df = load_job_data()

    st.sidebar.header("🔎 Apply Filters")
    locations = df['Location'].unique()
    job_types = df['Work Type'].unique()
    dates = df['Date'].unique()
    times = df['Time'].unique()

    selected_location = st.sidebar.selectbox("📍 Select Location", locations)
    selected_job_type = st.sidebar.selectbox("🛠 Select Job Type", job_types)
    selected_date = st.sidebar.selectbox("📅 Select Date", dates)
    selected_time = st.sidebar.selectbox("⏰ Select Time", times)
    keyword = st.sidebar.text_input("🔍 Search in Details")

    filtered_df = df[
        (df['Location'] == selected_location) &
        (df['Work Type'] == selected_job_type) &
        (df['Date'] == selected_date) &
        (df['Time'] == selected_time)
    ]

    if keyword:
        filtered_df = filtered_df[filtered_df['Details'].str.contains(keyword, case=False, na=False)]

    st.markdown("### ✅ Filtered Jobs")
    st.dataframe(filtered_df.style.set_properties(**{
        'border-color': 'black',
        'background-color': '#f9f9f9',
        'color': '#333'
    }))

    st.success(f"Showing {len(filtered_df)} matching jobs.")

    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Jobs as CSV", csv, file_name="filtered_jobs.csv", mime="text/csv")
    else:
        st.warning("⚠ No matching jobs found for selected filters.")

    # Download full data button
    csv_all = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download All Jobs", csv_all, file_name="all_jobs.csv", mime="text/csv")

if __name__ == '__main__':
    main()