import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib

from irrigation_logic import irrigation_advice  

# Load pre-trained models
crop_model = joblib.load('crop_recommendation_model.pkl')
weather_model = joblib.load('weather_prediction_model.pkl')

# Weather API configuration
API_KEY = "a54341456a66edadfce567ab9e85f0e8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

def get_current_weather(city_name):
    """Fetch current weather data from OpenWeatherMap API"""
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return temp, humidity
    else:
        return None, None

def get_user_city():
    """Auto-detect user's city using IP geolocation"""
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        city = data['city']
        return city
    except Exception as e:
        print(f"Error detecting location: {e}")
        return None

# Soil properties: [N, P, K, pH]
soil_properties = {
    'Sand':  [20, 10, 15, 6.5],
    'Clay':  [50, 40, 45, 6.0],
    'Loam':  [60, 50, 50, 6.5],
    'Chalk': [25, 15, 20, 7.5],
    'Peat':  [80, 60, 70, 5.5],
    'Silt':  [55, 45, 40, 6.3]
}

# Streamlit app configuration
st.set_page_config(page_title="Smart Farming Assistant", layout="centered")
st.title("🌾 Smart Farming Assistant")
st.write("Welcome! Get AI-powered Crop Recommendations or Irrigation Advice based on your location and soil type.")

# Main option selection
option = st.selectbox(
    'What would you like to do?',
    ('Select an option', 'Get Crop Recommendation', 'Get Irrigation Advice')
)

# Crop Recommendation Section
if option == 'Get Crop Recommendation':
    st.header("🌱 AI-Powered Crop Recommendation")

    soil_type = st.selectbox('Select Soil Type:', list(soil_properties.keys()))
    city = st.text_input('Enter City Name:')

    if st.button('Get AI Crop Recommendation'):
        if city:
            with st.spinner('Fetching real-time weather data...'):
                temp, humidity = get_current_weather(city)

            if temp is not None:
                st.write(f"🌡️ Current Temperature: {temp} °C")
                st.write(f"💧 Current Humidity: {humidity} %")

                # Get soil properties
                N, P, K, ph = soil_properties.get(soil_type)
                
                with st.spinner('Generating 30-day weather forecast...'):
                    # Generate future weather predictions
                    future_days = list(range(1, 31))
                    future_month = pd.Timestamp.now().month

                    # Create synthetic future weather data based on current conditions
                    future_data = pd.DataFrame({
                        'temp': np.random.normal(loc=temp, scale=2, size=30),
                        'humidity': np.random.normal(loc=humidity, scale=5, size=30),
                        'month': [future_month]*30,
                        'day': future_days
                    })

                    # Predict weather patterns
                    future_predictions = weather_model.predict(future_data)
                    label_map = {0: 'clear', 1: 'clouds', 2: 'rain'}
                    predicted_labels = [label_map[label] for label in future_predictions]

                    future_data['predicted_weather'] = predicted_labels
                    weather_counts = future_data['predicted_weather'].value_counts()

                    # Display weather forecast summary
                    st.subheader('🌦️ 30-Day Weather Forecast Summary:')
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("☀️ Clear Days", weather_counts.get('clear', 0))
                    with col2:
                        st.metric("☁️ Cloudy Days", weather_counts.get('clouds', 0))
                    with col3:
                        st.metric("🌧️ Rainy Days", weather_counts.get('rain', 0))

                # Prepare data for AI crop recommendation
                with st.spinner('Analyzing soil and weather data with AI...'):
                    # Calculate average future conditions
                    avg_future_temp = np.mean(future_data['temp'])
                    avg_future_humidity = np.mean(future_data['humidity'])
                    
                    # Estimate rainfall based on predicted rainy days
                    rain_days = weather_counts.get('rain', 0)
                    estimated_rainfall = rain_days * 8  # Estimate: 8mm per rainy day
                    
                    # Prepare features for the crop recommendation model
                    # Format: [N, P, K, temperature, humidity, pH, rainfall]
                    features = np.array([[N, P, K, avg_future_temp, avg_future_humidity, ph, estimated_rainfall]])
                    
                    # Get AI crop recommendation
                    try:
                        ai_crop_prediction = crop_model.predict(features)[0]
                        
                        # Display the main AI recommendation
                        st.success("🤖 AI Analysis Complete!")
                        st.subheader("🌱 Recommended Crop:")
                        
                        # Create an attractive display for the recommendation
                        st.markdown(f"""
                        <div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;">
                            <h2 style="color: #2e7d32; margin: 0;">🎯 {ai_crop_prediction}</h2>
                            <p style="color: #388e3c; margin: 5px 0 0 0;">Best crop for your conditions</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show detailed analysis
                        st.subheader("📊 Analysis Details:")
                        
                        analysis_col1, analysis_col2 = st.columns(2)
                        
                        with analysis_col1:
                            st.write("**Soil Analysis:**")
                            st.write(f"• Soil Type: {soil_type}")
                            st.write(f"• Nitrogen (N): {N} kg/ha")
                            st.write(f"• Phosphorus (P): {P} kg/ha")
                            st.write(f"• Potassium (K): {K} kg/ha")
                            st.write(f"• pH Level: {ph}")
                        
                        with analysis_col2:
                            st.write("**Weather Analysis:**")
                            st.write(f"• Avg Temperature: {avg_future_temp:.1f}°C")
                            st.write(f"• Avg Humidity: {avg_future_humidity:.1f}%")
                            st.write(f"• Expected Rainfall: {estimated_rainfall}mm")
                            st.write(f"• Rainy Days: {rain_days}/30")
                        
                        # Additional insights
                        st.info(f"💡 **Insight**: This recommendation is based on AI analysis of your soil composition ({soil_type}) and the predicted weather patterns for the next 30 days in {city}.")
                        
                    except Exception as e:
                        st.error(f"❌ Error in AI prediction: {str(e)}")
                        st.write("Please check if your model file is compatible with the input features.")

            else:
                st.error('❌ Could not fetch weather data. Please check the city name and try again.')

        else:
            st.warning('⚠️ Please enter your city name!')

# Irrigation Advice Section
elif option == 'Get Irrigation Advice':
    st.header("💧 Smart Irrigation Advice")

    location_choice = st.radio(
        "How would you like to provide your location?",
        ("Enter City Manually", "Use My Current Location")
    )

    if location_choice == "Enter City Manually":
        city = st.text_input('Enter City Name:')
    else:
        city = get_user_city()
        if city:
            st.success(f"📍 Detected City: {city}")
        else:
            st.error("❌ Could not detect your location. Please enter manually.")

    if st.button('Get Smart Irrigation Advice'):
        if city:
            with st.spinner('Analyzing current weather conditions...'):
                temp, humidity = get_current_weather(city)

            if temp is not None:
                st.write(f"🌡️ Current Temperature: {temp} °C")
                st.write(f"💧 Current Humidity: {humidity} %")

                try:
                    irrigation = irrigation_advice(temp, humidity)
                    
                    # Display irrigation advice with better formatting
                    st.success("💦 Smart Irrigation Recommendation:")
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                        <h3 style="color: #1976d2; margin: 0 0 10px 0;">🚿 {irrigation}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Additional context
                    if temp > 30:
                        st.warning("🌡️ High temperature detected - monitor soil moisture closely")
                    if humidity < 40:
                        st.warning("💨 Low humidity - plants may need extra water")
                    elif humidity > 80:
                        st.info("💧 High humidity - reduce watering frequency to prevent fungal issues")
                        
                except Exception as e:
                    st.error(f"❌ Error getting irrigation advice: {str(e)}")
            else:
                st.error('❌ Could not fetch weather data. Please check the city name.')
        else:
            st.warning('⚠️ Please provide a city or allow location detection.')

# Footer
st.markdown("---")
st.markdown("🌾 **Smart Farming Assistant** - Powered by AI and Real-time Weather Data")
