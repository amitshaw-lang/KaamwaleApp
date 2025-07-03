import streamlit as st

def main():
    # Title with style
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔒 Privacy Policy - KaamWale App</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Main content
    st.markdown("""
    **Effective Date:** 03 July 2025  

    ### 📝 1️⃣ Data Collection  
    KaamWale App collects the following data:
    - Name  
    - Phone Number  
    - Location (manual input)  
    - Job Details (Work type, Date, Time)  

    ### ⚙️ 2️⃣ Data Use  
    - To process customer job requests  
    - To assign jobs to workers  
    - To manage worker status in admin dashboard  

    ### 🔐 3️⃣ Data Sharing  
    - No data is shared with third parties  
    - Data is only shown between customers, workers, and admin for job assignment  

    ### 🛡 4️⃣ Data Security  
    - Data is stored securely in CSV files  
    - Only authorized admins have access  

    ### 🙋‍♂️ 5️⃣ User Rights  
    - You can request to update or delete your data anytime  
    - Contact us for any request  

    ### 📞 6️⃣ Contact  
    - **Email:** your-email@example.com  
    - **Phone:** +91-XXXXXXXXXX  
    """)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.success("✅ This is the complete privacy policy for KaamWale App.")

if __name__ == '__main__':
    main()