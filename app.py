import streamlit as st
import pandas as pd
import os
from datetime import date

# Page Layout Configuration
st.set_page_config(page_title="Trayambh Group", layout="wide")
st.title("🚜 Trayambh Group - Custom ERP (Project Shyamashray)")

# Database Files Setup
profile_file = "buffalo_profiles.csv"
milk_file = "milk_log.csv"
farm_file = "farm_daily_log.csv"

if not os.path.exists(profile_file):
    pd.DataFrame(columns=["Tag_ID", "Breed", "Date_Added"]).to_csv(profile_file, index=False)
if not os.path.exists(milk_file):
    pd.DataFrame(columns=["Date", "Tag_ID", "Morning_Milk_Kg", "Evening_Milk_Kg", "Total_Milk_Kg"]).to_csv(milk_file, index=False)
if not os.path.exists(farm_file):
    pd.DataFrame(columns=["Date", "Sale_Milk_Kg", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"]).to_csv(farm_file, index=False)

# ---------------- SIDEBAR NAVIGATION (PAGES) ---------------- #
st.sidebar.header("📁 Trayambh Departments")
page = st.sidebar.radio("Go To Page:", [
    "📊 Admin Dashboard (P&L)",
    "🐄 Dairy Farm (Cattle & Milk Log)",
    "🌾 Feed & Sales Entry",
    "🏭 Oil Mill Plant (Phase 2)",
    "🌱 Bio-Mass & Vedic Paint (Phase 2)"
])

# ==================== PAGE 1: ADMIN DASHBOARD ==================== #
if page == "📊 Admin Dashboard (P&L)":
    st.subheader("📊 Admin Financial Dashboard")
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if password == "trayambh123":
        try:
            milk_df = pd.read_csv(milk_file)
            farm_df = pd.read_csv(farm_file)
            
            if not milk_df.empty and not farm_df.empty:
                daily_milk = milk_df.groupby("Date")["Total_Milk_Kg"].sum().reset_index()
                farm_df = farm_df.drop_duplicates(subset=['Date'], keep='last')
                final_df = pd.merge(daily_milk, farm_df, on="Date", how="inner")
                
                if not final_df.empty:
                    # Buffalo Ghee Logic (15 Kg Milk = 1 Kg Ghee)
                    final_df['Milk_For_Ghee'] = final_df['Total_Milk_Kg'] - final_df['Sale_Milk_Kg']
                    final_df['Milk_For_Ghee'] = final_df['Milk_For_Ghee'].apply(lambda x: x if x > 0 else 0)
                    final_df['Ghee_Yield_Kg'] = final_df['Milk_For_Ghee'] / 15  
                    
                    # Revenues
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
                st.info("Abhi database mein data entry poori nahi hui hai.")
        except Exception as e:
            st.info("System fully functional hai. Kripya pehle baki pages par data entry karein.")
    elif password != "":
        st.error("Galat Password!")
    else:
        st.info("🔒 Ye page locked hai. Kripya sidebar mein Admin Password darj karein.")

# ==================== PAGE 2: DAIRY FARM ==================== #
elif page == "🐄 Dairy Farm (Cattle & Milk Log)":
    st.subheader("🐄 Dairy Farm Management")
    sub_tab1, sub_tab2 = st.tabs(["Buffalo Profiles", "Daily Milk Entry (Kg)"])
    
    with sub_tab1:
        st.markdown("### Add New Buffalo Profile")
        with st.form("add_buffalo"):
            tag_id = st.text_input("Buffalo Tag ID (Example: B-001)")
            breed = st.selectbox("Breed", ["Murrah", "Jafarabadi", "Surti", "Other"])
            if st.form_submit_button("Save Profile"):
                if tag_id:
                    pd.DataFrame([[tag_id, breed, date.today()]], columns=["Tag_ID", "Breed", "Date_Added"]).to_csv(profile_file, mode='a', header=False, index=False)
                    st.success(f"Buffalo {tag_id} ki profile successfully save ho gayi!")
                    
    with sub_tab2:
        st.markdown("### Daily Milk Log (Per Buffalo in Kg)")
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
                    st.success(f"Tag {selected_tag} ka total {total_kg} Kg doodh register ho gaya!")
        else:
            st.warning("⚠️ Pehle 'Buffalo Profiles' tab mein jaakar kam se kam ek Buffalo register karein.")

# ==================== PAGE 3: FEED & SALES ==================== #
elif page == "🌾 Feed & Sales Entry":
    st.subheader("🌾 Daily Farm Feed & Sales Entry")
    with st.form("feed_sales"):
        st.markdown("**Today's Total Feed Consumption**")
        col1, col2, col3 = st.columns(3)
        hydro = col1.number_input("Hydroponics Consumed (Kg)", min_value=0.0)
        azolla = col2.number_input("Azolla Consumed (Kg)", min_value=0.0)
        cattle_feed = col3.number_input("Cattle Feed / Pellets (Kg)", min_value=0.0)
        
        feed_cost = st.number_input("Total Farm Feed Cost Today (₹)", min_value=0.0)
        
        st.markdown("**Direct Milk Sales**")
        sale_milk = st.number_input("Total Milk Allocated for Direct Sale Today (Kg)", min_value=0.0)
        
        if st.form_submit_button("Save Feed & Sales Data"):
            pd.DataFrame([[date.today(), sale_milk, hydro, azolla, cattle_feed, feed_cost]], columns=["Date", "Sale_Milk_Kg", "Hydroponics_Kg", "Azolla_Kg", "Cattle_Feed_Kg", "Feed_Cost"]).to_csv(farm_file, mode='a', header=False, index=False)
            st.success("Feed aur Sales ka daily data successfully save ho gaya!")

# ==================== PAGE 4: OIL MILL PLACEHOLDER ==================== #
elif page == "🏭 Oil Mill Plant (Phase 2)":
    st.subheader("🏭 Oil Mill Plant Department")
    st.info("🚧 Welcome to Trayambh Oil Mill System! This department is currently locked for Phase 2.")
    st.markdown("""
    ### 📋 Planned Features for this Page:
    * **Seed Crushing Logs:** Mustard, Soybean, ya Cottonseed procurement aur crushing ka daily data tracking.
    * **Oil & Khal Yield Tracker:** Kitne seed se kitna litre pure oil nikla aur kitne quintal Khal (Cattle Feed cake) bani.
    * **Inventory Link:** Tel ka export/local sales aur bachi hui Khal ka sidha humare feed system mein transfer automatic record hoga.
    """)

# ==================== PAGE 5: BIOMASS PLACEHOLDER ==================== #
elif page == "🌱 Bio-Mass & Vedic Paint (Phase 2)":
    st.subheader("🌱 Bio-Mass & Vedic Paint Department")
    st.info("🚧 Welcome to Trayambh Waste-to-Energy System! This department is currently locked for Phase 2.")
    st.markdown("""
    ### 📋 Planned Features for this Page:
    * **Cow-Dung Stock Records:** Daily total dung accumulation aur procurement tracker.
    * **Vedic Paint Manufacturing:** Paint production batches, formulations, raw material cost aur chemical analytics.
    * **Biogas & Slurry Logs:** Gas production efficiency aur bio-fertilizer/slurry sales ka automatic P&L.
    """)
