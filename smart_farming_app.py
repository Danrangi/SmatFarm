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
        return None

# Soil properties: [N, P, K, pH]
soil_properties = {
    'Sandy Soil (Light soil, drains fast)': [20, 10, 15, 6.5],
    'Clay Soil (Heavy soil, holds water)': [50, 40, 45, 6.0],
    'Loam Soil (Good for most crops)': [60, 50, 50, 6.5],
    'Chalky Soil (Rocky, alkaline)': [25, 15, 20, 7.5],
    'Peat Soil (Dark, organic)': [80, 60, 70, 5.5],
    'Silty Soil (Smooth, fertile)': [55, 45, 40, 6.3]
}

# Streamlit app configuration
st.set_page_config(page_title="Smart Farming Helper", layout="centered")

# Simple header
st.title("🌾 Smart Farming Helper")
st.write("Get help with farming decisions")

# Simple main menu
st.subheader("What do you need help with?")
option = st.selectbox(
    '',
    ('Choose what you need', 'What crop should I plant?', 'When should I water my crops?')
)

# Crop Recommendation Section
if option == 'What crop should I plant?':
    st.header("🌱 Find the Best Crop for You")
    
    # Simple soil selection
    st.write("**Step 1: What type of soil do you have?**")
    soil_type = st.selectbox('Choose your soil type:', list(soil_properties.keys()))
    
    # Simple city input
    st.write("**Step 2: Where are you located?**")
    city = st.text_input('Enter your city name:')
    
    # Simple button
    if st.button('Find Best Crop', type="primary"):
        if city:
            # Show loading message
            st.info('Getting weather information...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                # Show current weather simply
                st.success(f"Weather in {city}: {temp}°C, Humidity: {humidity}%")

                # Get soil properties
                N, P, K, ph = soil_properties.get(soil_type)
                
                st.info('Checking weather for next month...')
                
                # Generate future weather predictions
                future_data = pd.DataFrame({
                    'temp': np.random.normal(loc=temp, scale=2, size=30),
                    'humidity': np.random.normal(loc=humidity, scale=5, size=30),
                    'month': [pd.Timestamp.now().month]*30,
                    'day': list(range(1, 31))
                })

                # Predict weather patterns
                future_predictions = weather_model.predict(future_data)
                label_map = {0: 'clear', 1: 'clouds', 2: 'rain'}
                predicted_labels = [label_map[label] for label in future_predictions]
                future_data['predicted_weather'] = predicted_labels
                weather_counts = future_data['predicted_weather'].value_counts()

                # Calculate conditions for AI model
                avg_temp = np.mean(future_data['temp'])
                avg_humidity = np.mean(future_data['humidity'])
                rain_days = weather_counts.get('rain', 0)
                estimated_rainfall = rain_days * 8
                
                st.info('Finding the best crop for you...')
                
                # Get AI crop recommendation
                try:
                    features = np.array([[N, P, K, avg_temp, avg_humidity, ph, estimated_rainfall]])
                    recommended_crop = crop_model.predict(features)[0]
                    
                    # Show simple result
                    st.success("✅ Done!")
                    
                    # Big, clear recommendation
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #155724; margin: 0; font-size: 2.5em;">🌾 {recommended_crop}</h1>
                        <h3 style="color: #155724; margin: 10px 0 0 0;">This is the best crop for you!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Simple weather summary
                    st.write("**Weather Summary for Next Month:**")
                    st.write(f"☀️ Sunny days: {weather_counts.get('clear', 0)}")
                    st.write(f"☁️ Cloudy days: {weather_counts.get('clouds', 0)}")
                    st.write(f"🌧️ Rainy days: {rain_days}")
                    
                except Exception as e:
                    st.error("Sorry, something went wrong. Please try again.")

            else:
                st.error('Could not get weather information. Please check your city name.')

        else:
            st.warning('Please enter your city name.')

# Irrigation Advice Section
elif option == 'When should I water my crops?':
    st.header("💧 Watering Advice")
    
    st.write("**Where are you located?**")
    
    # Simple location options
    location_choice = st.radio(
        "",
        ("I will type my city", "Find my location automatically")
    )

    if location_choice == "I will type my city":
        city = st.text_input('Enter your city name:')
    else:
        city = get_user_city()
        if city:
            st.success(f"Found your location: {city}")
        else:
            st.error("Could not find your location. Please type your city name.")
            city = st.text_input('Enter your city name:')

    if st.button('Get Watering Advice', type="primary"):
        if city:
            st.info('Checking current weather...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                # Show current conditions simply
                st.write(f"**Current weather in {city}:**")
                st.write(f"🌡️ Temperature: {temp}°C")
                st.write(f"💧 Humidity: {humidity}%")

                try:
                    irrigation = irrigation_advice(temp, humidity)
                    
                    # Show simple watering advice
                    st.success("✅ Here's your watering advice:")
                    
                    st.markdown(f"""
                    <div style="background-color: #cce7ff; padding: 25px; border-radius: 10px; text-align: center;">
                        <h2 style="color: #004085; margin: 0;">💦 {irrigation}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error("Sorry, could not get watering advice. Please try again.")
            else:
                st.error('Could not get weather information. Please check your city name.')
        else:
            st.warning('Please enter your city name.')

# Simple footer
if option == 'Choose what you need':
    st.info("👆 Please choose what you need help with from the dropdown above.")

st.markdown("---")
st.write("🌾 Smart Farming Helper - Making farming easier for everyone")
