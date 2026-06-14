import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Trayambh Dairy", layout="wide")
st.title("🥛 Trayambh Dairy (Project Shyamashray)")

# 3 Files banengi (Profile ke liye, Milk ke liye, aur Feed/Sales ke liye)
profile_file = "buffalo_profiles.csv"
milk_file = "milk_log.csv"
farm_file = "farm_daily_log.csv"

# Agar file nahi hai toh naya database create karein
if not os.path.exists(profile_file):
    pd.DataFrame(columns=["Tag_ID", "Breed", "Date_Added"]).to_csv(profile_file, index=False)
if not os.path.exists(milk_file):
    pd.DataFrame(columns=["Date", "Tag_ID", "Morning_Milk_Kg", "Evening_Milk_Kg", "Total_Milk_Kg"]).to_csv(milk_file, index=False)
if not os.path.exists(farm_file):
    pd.DataFrame(columns=["Date", "Sale_Milk_Kg", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"]).to_csv(farm_file, index=False)

st.sidebar.header("Login / Role")
user_role = st.sidebar.radio("Select User:", ["Employee (Data Entry)", "Admin (Owner)"])

# ---------------- EMPLOYEE VIEW ---------------- #
if user_role == "Employee (Data Entry)":
    # 3 Tabs: Profile, Milk, aur purana wala Feed/Sale section
    tab1, tab2, tab3 = st.tabs(["🐄 Add Buffalo", "⚖️ Daily Milk (Kg)", "🌾 Feed & Sales Entry"])
    
    with tab1:
        st.subheader("Add New Buffalo Profile")
        with st.form("add_buffalo"):
            tag_id = st.text_input("Buffalo Tag ID (Example: B-001)")
            breed = st.selectbox("Breed", ["Murrah", "Jafarabadi", "Surti", "Other"])
            
            if st.form_submit_button("Save Profile"):
                if tag_id:
                    pd.DataFrame([[tag_id, breed, date.today()]], columns=["Tag_ID", "Breed", "Date_Added"]).to_csv(profile_file, mode='a', header=False, index=False)
                    st.success(f"Buffalo {tag_id} ki profile ban gayi!")
                    
    with tab2:
        st.subheader("Daily Milk Log (Per Buffalo)")
        profiles_df = pd.read_csv(profile_file)
        
        if not profiles_df.empty:
            with st.form("milk_entry"):
                selected_tag = st.selectbox("Select Buffalo Tag ID", profiles_df["Tag_ID"].tolist())
                c1, c2 = st.columns(2)
                morning_kg = c1.number_input("Morning Milk (Kg)", min_value=0.0, step=0.1)
                evening_kg = c2.number_input("Evening Milk (Kg)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("Save Milk Data"):
                    total_kg = morning_kg + evening_kg
                    pd.DataFrame([[date.today(), selected_tag, morning_kg, evening_kg, total_kg]], columns=["Date", "Tag_ID", "Morning_Milk_Kg", "Evening_Milk_Kg", "Total_Milk_Kg"]).to_csv(milk_file, mode='a', header=False, index=False)
                    st.success(f"Tag {selected_tag} ka total {total_kg} Kg doodh save ho gaya!")
        else:
            st.warning("Pehle Tab 1 mein jaakar kam se kam ek Buffalo add karein.")
            
    with tab3:
        st.subheader("Daily Farm Feed & Sales (Financial Entry)")
        with st.form("feed_sales"):
            st.markdown("**Today's Total Feed Consumption**")
            col1, col2, col3 = st.columns(3)
            hydro = col1.number_input("Hydroponics (Kg)", min_value=0.0)
            azolla = col2.number_input("Azolla (Kg)", min_value=0.0)
            cattle_feed = col3.number_input("Cattle Feed (Kg)", min_value=0.0)
            
            feed_cost = st.number_input("Total Farm Feed Cost Today (₹)", min_value=0.0)
            
            st.markdown("**Direct Milk Sales**")
            sale_milk = st.number_input("Total Milk Allocated for Direct Sale Today (Kg)", min_value=0.0)
            
            if st.form_submit_button("Save Feed & Sales Data"):
                pd.DataFrame([[date.today(), sale_milk, hydro, azolla, cattle_feed, feed_cost]], columns=["Date", "Sale_Milk_Kg", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"]).to_csv(farm_file, mode='a', header=False, index=False)
                st.success("Aaj ka Feed aur Sales ka data save ho gaya!")

# ---------------- ADMIN VIEW ---------------- #
elif user_role == "Admin (Owner)":
    st.subheader("📊 Admin Financial Dashboard (Ghee & P&L)")
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if password == "trayambh123":
        try:
            milk_df = pd.read_csv(milk_file)
            farm_df = pd.read_csv(farm_file)
            
            if not milk_df.empty and not farm_df.empty:
                # Har din ka total farm milk calculate karna
                daily_milk = milk_df.groupby("Date")["Total_Milk_Kg"].sum().reset_index()
                
                # Farm ke baaki data (Feed/Sales) ke sath merge karna
                farm_df = farm_df.drop_duplicates(subset=['Date'], keep='last')
                final_df = pd.merge(daily_milk, farm_df, on="Date", how="inner")
                
                if not final_df.empty:
                    # Ghee ka calculation (15 Kg = 1 Kg Ghee)
                    final_df['Milk_For_Ghee'] = final_df['Total_Milk_Kg'] - final_df['Sale_Milk_Kg']
                    final_df['Milk_For_Ghee'] = final_df['Milk_For_Ghee'].apply(lambda x: x if x > 0 else 0)
                    final_df['Ghee_Yield_Kg'] = final_df['Milk_For_Ghee'] / 15  
                    
                    # Profit & Loss
                    final_df['Milk_Revenue'] = final_df['Sale_Milk_Kg'] * 65 # ₹65/Kg Milk
                    final_df['Ghee_Revenue'] = final_df['Ghee_Yield_Kg'] * 1000 # ₹1000/Kg Ghee
                    final_df['Net_Profit'] = (final_df['Milk_Revenue'] + final_df['Ghee_Revenue']) - final_df['Feed_Cost']
                    
                    st.markdown("### 💰 Daily Profit & Loss Statement")
                    st.dataframe(final_df[["Date", "Total_Milk_Kg", "Feed_Cost", "Milk_Revenue", "Ghee_Revenue", "Net_Profit"]])
                    
                    st.markdown("### 📈 Net Profit Trends")
                    st.bar_chart(final_df[['Date', 'Net_Profit']].set_index('Date'))
                else:
                    st.info("Kripya aaj ka Milk aur Feed dono entry poori karein.")
            else:
                st.info("Abhi data entry poori nahi hui hai.")
        except Exception as e:
            st.error("System Ready ho raha hai, kripya employee view me jaakar entry karein.")
