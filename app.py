import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Trayambh Dairy", layout="wide")
st.title("🥛 Trayambh Dairy Management (Project Shyamashray)")

# Data file (Abhi cloud testing ke liye CSV use kar rahe hain)
data_file = "trayambh_data.csv"
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Date", "Total_Buffaloes", "Total_Milk", "Sale_Milk", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"])
    df.to_csv(data_file, index=False)

st.sidebar.header("Login / Role")
user_role = st.sidebar.radio("Select User:", ["Employee (Data Entry)", "Admin (Owner)"])

# --- EMPLOYEE VIEW ---
if user_role == "Employee (Data Entry)":
    st.subheader("📝 Daily Farm Entry (Buffaloes)")
    
    with st.form("daily_entry"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Buffalo & Milk Log**")
            buffalo_count = st.number_input("Total Milking Buffaloes", min_value=0, value=50)
            total_milk = st.number_input("Total Milk Produced (Liters)", min_value=0.0, value=0.0)
            sale_milk = st.number_input("Milk for Direct Sale (Liters)", min_value=0.0, value=0.0)
            
        with col2:
            st.markdown("**Feed Management**")
            hydroponics = st.number_input("Hydroponics Consumed (Kg)", min_value=0.0, value=0.0)
            azolla = st.number_input("Azolla Consumed (Kg)", min_value=0.0, value=0.0)
            cattle_feed = st.number_input("Cattle Feed/Pellets (Kg)", min_value=0.0, value=0.0)
            feed_cost = st.number_input("Total Feed Cost Today (₹)", min_value=0.0, value=0.0)
            
        if st.form_submit_button("Save Daily Data"):
            new_data = pd.DataFrame([[date.today(), buffalo_count, total_milk, sale_milk, hydroponics, azolla, cattle_feed, feed_cost]], 
                                    columns=["Date", "Total_Buffaloes", "Total_Milk", "Sale_Milk", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"])
            new_data.to_csv(data_file, mode='a', header=False, index=False)
            st.success("Aaj ka data successfully save ho gaya!")

# --- ADMIN VIEW ---
elif user_role == "Admin (Owner)":
    st.subheader("📊 Admin Financial Dashboard")
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if password == "trayambh123": # Ye aapka testing password hai
        df = pd.read_csv(data_file)
        if not df.empty:
            st.markdown("### Daily Profit & Loss")
            df['Milk_For_Ghee'] = df['Total_Milk'] - df['Sale_Milk']
            df['Ghee_Yield_Kg'] = df['Milk_For_Ghee'] / 15  # Buffalo Ghee ratio (15L = 1Kg)
            
            df['Milk_Revenue'] = df['Sale_Milk'] * 65 # ₹65/L
            df['Ghee_Revenue'] = df['Ghee_Yield_Kg'] * 1000  # ₹1000/Kg Ghee
            df['Net_Profit'] = (df['Milk_Revenue'] + df['Ghee_Revenue']) - df['Feed_Cost']
            
            st.dataframe(df)
            st.bar_chart(df[['Date', 'Net_Profit']].set_index('Date'))
        else:
            st.info("Abhi tak koi data enter nahi hua hai.")
