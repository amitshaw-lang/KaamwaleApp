import pandas as pd
import streamlit as st

def load_job_data():
    return pd.read_csv('job_requests.csv')

def main():
    st.title("Job Filter System")
    
    df = load_job_data()
    
    locations = df['Location'].unique()
    job_types = df['JobType'].unique()
    
    selected_location = st.selectbox("Select Location", locations)
    selected_job_type = st.selectbox("Select Job Type", job_types)
    
    filtered_df = df[
        (df['Location'] == selected_location) &
        (df['JobType'] == selected_job_type)
    ]
    
    st.write("Filtered Jobs", filtered_df)

if __name__ == '__main__':
    main()