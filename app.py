import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Trayambh Dairy", layout="wide")
st.title("🥛 Trayambh Dairy (Project Shyamashray)")

# Nayi files (Taaki purane data se clash na ho)
profile_file = "buffalo_profiles.csv"
milk_log_file = "milk_log.csv"

# Agar file nahi hai toh naya database create karein
if not os.path.exists(profile_file):
    pd.DataFrame(columns=["Tag_ID", "Breed", "Date_Added"]).to_csv(profile_file, index=False)
if not os.path.exists(milk_log_file):
    pd.DataFrame(columns=["Date", "Tag_ID", "Morning_Milk_Kg", "Evening_Milk_Kg", "Total_Milk_Kg"]).to_csv(milk_log_file, index=False)

st.sidebar.header("Login / Role")
user_role = st.sidebar.radio("Select User:", ["Employee (Data Entry)", "Admin (Owner)"])

# ---------------- EMPLOYEE VIEW ---------------- #
if user_role == "Employee (Data Entry)":
    # App ko aur sundar banane ke liye Tabs ka use
    tab1, tab2 = st.tabs(["🐄 Manage Buffalo Profiles", "⚖️ Daily Milk Entry (Kg)"])
    
    with tab1:
        st.subheader("Add New Buffalo")
        with st.form("add_buffalo"):
            tag_id = st.text_input("Buffalo Tag ID / Number (Example: B-001)")
            breed = st.selectbox("Breed", ["Murrah", "Jafarabadi", "Surti", "Other"])
            
            if st.form_submit_button("Save Profile"):
                if tag_id:
                    new_prof = pd.DataFrame([[tag_id, breed, date.today()]], columns=["Tag_ID", "Breed", "Date_Added"])
                    new_prof.to_csv(profile_file, mode='a', header=False, index=False)
                    st.success(f"Buffalo {tag_id} ki profile ban gayi!")
                else:
                    st.error("Please enter a Tag ID")
                    
    with tab2:
        st.subheader("Daily Milk Log (Per Buffalo)")
        profiles_df = pd.read_csv(profile_file)
        
        if profiles_df.empty:
            st.warning("Data Entry se pehle Tab 1 mein jaakar kam se kam ek Buffalo ki profile add karein.")
        else:
            with st.form("milk_entry"):
                # Dropdown menu jisme saari bhainso ke Tag ID aayenge
                selected_tag = st.selectbox("Select Buffalo Tag ID", profiles_df["Tag_ID"].tolist())
                
                col1, col2 = st.columns(2)
                with col1:
                    morning_kg = st.number_input("Morning Milk (Kg)", min_value=0.0, value=0.0, step=0.1)
                with col2:
                    evening_kg = st.number_input("Evening Milk (Kg)", min_value=0.0, value=0.0, step=0.1)
                
                if st.form_submit_button("Save Milk Data"):
                    total_kg = morning_kg + evening_kg
                    new_log = pd.DataFrame([[date.today(), selected_tag, morning_kg, evening_kg, total_kg]], 
                                           columns=["Date", "Tag_ID", "Morning_Milk_Kg", "Evening_Milk_Kg", "Total_Milk_Kg"])
                    new_log.to_csv(milk_log_file, mode='a', header=False, index=False)
                    st.success(f"Tag {selected_tag} ka total {total_kg} Kg doodh save ho gaya!")

# ---------------- ADMIN VIEW ---------------- #
elif user_role == "Admin (Owner)":
    st.subheader("📊 Admin Dashboard (Milk Analytics)")
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if password == "trayambh123":
        try:
            milk_df = pd.read_csv(milk_log_file)
            if not milk_df.empty:
                st.markdown("### 📈 Detailed Milk Production Data")
                st.dataframe(milk_df)
                
                # Chart: Har din ka total farm production
                daily_total = milk_df.groupby("Date")["Total_Milk_Kg"].sum().reset_index()
                st.markdown("### Total Daily Farm Production (Kg)")
                st.bar_chart(daily_total.set_index("Date"))
            else:
                st.info("Abhi doodh ki koi entry nahi hui hai.")
        except Exception as e:
            st.info("System Ready ho raha hai, kripya pehli entry karein.")
