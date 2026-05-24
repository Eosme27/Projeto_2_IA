import streamlit as st
import pandas as pd
import joblib
import os

# Set page config FIRST
st.set_page_config(page_title="RealEstate AI", layout="centered")

# --- ADVANCED SaaS CSS INJECTION ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"]  { font-family: 'Inter', sans-serif !important; color: #111827 !important; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
            border-radius: 6px !important; border: 1px solid #D1D5DB !important;
            background-color: #F9FAFB !important; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05) !important;
        }
        .stButton>button { 
            background-color: #111827 !important; color: #FFFFFF !important; 
            width: 100%; border-radius: 6px !important; border: none !important;
            padding: 0.6rem 1rem !important; font-weight: 600 !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; transition: all 0.2s ease !important;
        }
        .stButton>button:hover { background-color: #374151 !important; transform: translateY(-1px) !important; }
        .stAlert { border-radius: 8px !important; border: 1px solid #E5E7EB !important; background-color: #FFFFFF !important; }
        h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.02em !important; }
    </style>
""", unsafe_allow_html=True)


# --- DATA LOADING ---
@st.cache_data
def load_locations():
    try:
        df = pd.read_csv("portugal_listinigs.csv")
        porto_df = df[df['District'] == 'Porto']
        cities = sorted(porto_df['City'].dropna().unique().tolist())
        return cities
    except FileNotFoundError:
        return ["Porto", "Maia", "Matosinhos", "Vila Nova de Gaia", "Gondomar"]

cities = load_locations()

st.title("🏠 Porto Property Value Estimator")
st.write("Enter the property details below to get an instant valuation.")

# --- INPUT FORM ---
st.header("Property Features")

# Row 1: Location & Type
col1, col2, col3 = st.columns(3)
with col1:
    city = st.selectbox("City", cities)
with col2:
    town = st.text_input("Town (Parish)", value="Paranhos") # Added Town
with col3:
    property_type = st.selectbox("Property Type", ["Apartment", "House"])

# Row 2: Areas
col4, col5, col6 = st.columns(3)
with col4:
    gross_area = st.number_input("Gross Area (m²)", min_value=10, value=120)
with col5:
    total_area = st.number_input("Total Area (m²)", min_value=10, value=150) # Added TotalArea
with col6:
    living_area = st.number_input("Living Area (m²)", min_value=10, value=100) # Added LivingArea

# Row 3: Rooms & Parking Count
col7, col8, col9 = st.columns(3)
with col7:
    bedrooms = st.number_input("Bedrooms", min_value=0, value=2)
with col8:
    bathrooms = st.number_input("Bathrooms", min_value=1, value=2)
with col9:
    parking_spots = st.number_input("Parking Spots", min_value=0, value=1) # Added Parking

# Row 4: Specs & Year
col10, col11, col12 = st.columns(3)
with col10:
    energy_cert = st.selectbox("Energy Rating", ["A+", "A", "B", "C", "D", "E", "F"])
with col11:
    conservation = st.selectbox("Condition", ["New", "Like new", "Good condition", "Used", "Needs renovation"])
with col12:
    construction_year = st.number_input("Year Built", min_value=1800, max_value=2025, value=2000) # Added ConstructionYear

# Row 5: Booleans
col13, col14 = st.columns(2)
with col13:
    has_parking = st.checkbox("Has Parking Facility", value=True)
with col14:
    has_elevator = st.checkbox("Building has Elevator", value=True) # Added Elevator

# --- PREDICTION LOGIC ---
st.markdown("---")
if st.button("Predict Price"):
    try:
        # 1. Routing Logic
        file_name = 'porto_apartments_rf_model.pkl' if property_type == "Apartment" else 'porto_houses_rf_model.pkl'
        
        if os.path.exists(f"models/{file_name}"):
            model_path = f"models/{file_name}"
        elif os.path.exists(f"../models/{file_name}"):
            model_path = f"../models/{file_name}"
        else:
            raise FileNotFoundError(f"Could not find {file_name} in the models/ directory.")

        model = joblib.load(model_path)
        
        # 2. Package inputs EXACTLY how your friend's model expects them!
        # Order and exact naming matters heavily here.
        input_data = pd.DataFrame({
            'City': [city],
            'Town': [town],
            'Type': [property_type],
            'EnergyCertificate': [energy_cert],
            'GrossArea': [gross_area],
            'TotalArea': [total_area],
            'Parking': [parking_spots],
            'HasParking': [has_parking],
            'Elevator': [has_elevator],
            'ConstructionYear': [construction_year],
            'NumberOfBedrooms': [bedrooms],
            'ConservationStatus': [conservation],
            'LivingArea': [living_area],
            'NumberOfBathrooms': [bathrooms]
        })
        
        # 3. Get the real AI prediction
        predicted_price = model.predict(input_data)[0]

        # 4. Output UI
        st.success(f"✅ Valuation generated using our specialized {property_type} AI.")
        
        res_col1, res_col2 = st.columns([2, 1])
        with res_col1:
            st.metric(label="Estimated Market Value", value=f"€ {predicted_price:,.0f}")
            st.caption(f"💡 *Expected negotiation range is between **€ {(predicted_price*0.95):,.0f}** and **€ {(predicted_price*1.05):,.0f}**.*")
            
        with res_col2:
            st.markdown(f"""
            **Summary:**
            * **Type:** {property_type}
            * **Year:** {construction_year}
            * **Size:** {gross_area} m² 
            """)
            
        st.balloons()
        
    except FileNotFoundError as e:
        st.error(f"🚨 {e}")
    except Exception as e:
        st.error(f"🚨 Prediction Error: {e}")