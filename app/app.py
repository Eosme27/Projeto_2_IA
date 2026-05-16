import streamlit as st
import pandas as pd
import joblib

# Set page config FIRST
st.set_page_config(page_title="RealEstate AI", layout="centered")

# --- ADVANCED SaaS CSS INJECTION ---
st.markdown("""
    <style>
        /* Import font (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Apply the font globally */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif !important;
            color: #111827 !important; /* Dark slate text */
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Style the input boxes, dropdowns, and sliders */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div {
            border-radius: 6px !important;
            border: 1px solid #D1D5DB !important;
            background-color: #F9FAFB !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease;
        }

        /* Hover & Focus states for inputs */
        div[data-baseweb="input"] > div:hover, 
        div[data-baseweb="select"] > div:hover {
            border-color: #9CA3AF !important;
        }
        
        /* Button Styling (Dark/Sleek look) */
        .stButton>button { 
            background-color: #111827 !important; 
            color: #FFFFFF !important; 
            width: 100%; 
            border-radius: 6px !important; 
            border: none !important;
            padding: 0.6rem 1rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            transition: all 0.2s ease !important;
        }

        /* Button Hover Effect */
        .stButton>button:hover {
            background-color: #374151 !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
            transform: translateY(-1px) !important;
        }

        /* Clean up the Success Message Box */
        .stAlert {
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Subtitles and Headers */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
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

# Row 1: Location and Type
col1, col2 = st.columns(2)
with col1:
    city = st.selectbox("City (Porto District)", cities)
    property_type = st.selectbox("Property Type", ["Apartment", "House", "Duplex", "Studio"])
with col2:
    gross_area = st.number_input("Gross Area (m²)", min_value=10, max_value=1000, value=100)
    energy_cert = st.selectbox("Energy Certificate", ["A+", "A", "B", "C", "D", "E", "F"])

# Row 2: Rooms and Status
col3, col4 = st.columns(2)
with col3:
    bedrooms = st.slider("Bedrooms", 0, 6, 2)
    bathrooms = st.slider("Bathrooms", 1, 5, 2)
with col4:
    conservation = st.selectbox("Conservation Status", ["New", "Like new", "Good condition", "Used", "Needs renovation"])
    has_parking = st.checkbox("Has Parking / Garage")

# --- PREDICTION LOGIC ---
st.markdown("---")
if st.button("Predict Price"):
    try:
        # 1. Load the ML model (Wait for your ML engineer to finish this)
        # model = joblib.load('models/modelo.pkl')
        
        # 2. Package inputs exactly how the scikit-learn model will expect them
        input_data = pd.DataFrame({
            'City': [city],
            'Type': [property_type],
            'GrossArea': [gross_area],
            'EnergyCertificate': [energy_cert],
            'NumberOfBedrooms': [bedrooms],
            'NumberOfBathrooms': [bathrooms],
            'ConservationStatus': [conservation],
            'HasParking': [has_parking]
        })
        
        # 3. Mock calculation so you can test the UI right now
        base_price = 50000
        price_per_m2 = 3500 if city in ["Porto", "Matosinhos"] else 2000
        mock_price = base_price + (gross_area * price_per_m2) + (bedrooms * 10000)
        
        # Give a bonus to newer properties
        if conservation in ["New", "Like new"]:
            mock_price *= 1.15 

        st.success(f"### Estimated Market Price: € {mock_price:,.2f}")
        st.balloons()
        
    except FileNotFoundError:
        st.error("Model file not found.")