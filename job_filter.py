import pandas as pd
import streamlit as st

def load_job_data():
    return pd.read_csv('job_requests.csv')

def main():
    st.title("Job Filter System")

    df = load_job_data()

    locations = df['Location'].unique()
    job_types = df['Work Type'].unique()
    dates = df['Date'].unique()
    times = df['Time'].unique()

    selected_location = st.selectbox("Select Location", locations)
    selected_job_type = st.selectbox("Select Job Type", job_types)
    selected_date = st.selectbox("Select Date", dates)
    selected_time = st.selectbox("Select Time", times)

    filtered_df = df[
        (df['Location'] == selected_location) &
        (df['Work Type'] == selected_job_type) &
        (df['Date'] == selected_date) &
        (df['Time'] == selected_time)
    ]

    st.write("Filtered Jobs", filtered_df)

if __name__ == '__main__':
    main()