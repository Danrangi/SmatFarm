import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib

from irrigation_logic import irrigation_advice  

# Load models
crop_model = joblib.load('crop_recommendation_model.pkl')
weather_model = joblib.load('weather_prediction_model.pkl')

# Weather API
API_KEY = "a54341456a66edadfce567ab9e85f0e8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

def get_current_weather(city_name):
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
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        city = data['city']
        return city
    except Exception as e:
        return None

# Simple soil types
soil_types = {
    'Sandy (drains water quickly)': [20, 10, 15, 6.5],
    'Clay (holds water well)': [50, 40, 45, 6.0],
    'Mixed (good for most plants)': [60, 50, 50, 6.5],
    'Rocky': [25, 15, 20, 7.5],
    'Dark rich soil': [80, 60, 70, 5.5],
    'Smooth fine soil': [55, 45, 40, 6.3]
}

# App setup
st.set_page_config(page_title="Farm Helper", layout="centered")

st.title("🌾 Farm Helper")
st.write("Get help with your farming")

# Main menu
st.subheader("What do you need?")
choice = st.selectbox(
    '',
    ('Select', 'What should I plant?', 'When should I water?')
)

# Plant recommendation
if choice == 'What should I plant?':
    st.header("🌱 Find What to Plant")
    
    st.write("**What type of soil do you have?**")
    soil = st.selectbox('Pick your soil:', list(soil_types.keys()))
    
    st.write("**What city are you in?**")
    city = st.text_input('Type your city:')
    
    if st.button('Tell Me What to Plant', type="primary"):
        if city:
            st.info('Checking weather...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                st.success(f"Weather: {temp}°C")

                # Get soil info
                N, P, K, ph = soil_types.get(soil)
                
                st.info('Looking at weather for coming weeks...')
                
                # Future weather
                future_data = pd.DataFrame({
                    'temp': np.random.normal(loc=temp, scale=2, size=30),
                    'humidity': np.random.normal(loc=humidity, scale=5, size=30),
                    'month': [pd.Timestamp.now().month]*30,
                    'day': list(range(1, 31))
                })

                future_predictions = weather_model.predict(future_data)
                label_map = {0: 'clear', 1: 'clouds', 2: 'rain'}
                predicted_labels = [label_map[label] for label in future_predictions]
                future_data['predicted_weather'] = predicted_labels
                weather_counts = future_data['predicted_weather'].value_counts()

                # Calculate for AI
                avg_temp = np.mean(future_data['temp'])
                avg_humidity = np.mean(future_data['humidity'])
                rain_days = weather_counts.get('rain', 0)
                rainfall = rain_days * 8
                
                st.info('Finding best plant for you...')
                
                try:
                    features = np.array([[N, P, K, avg_temp, avg_humidity, ph, rainfall]])
                    best_crop = crop_model.predict(features)[0]
                    
                    st.success("Done!")
                    
                    # Show result
                    st.markdown(f"""
                    <div style="background-color: #e8f5e8; padding: 40px; border-radius: 20px; text-align: center;">
                        <h1 style="color: #2e7d32; margin: 0; font-size: 3em;">🌾</h1>
                        <h1 style="color: #2e7d32; margin: 10px 0;">{best_crop}</h1>
                        <h3 style="color: #388e3c; margin: 0;">Plant this!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Simple weather info
                    sunny = weather_counts.get('clear', 0)
                    cloudy = weather_counts.get('clouds', 0)
                    rainy = rain_days
                    
                    st.write("**Weather coming up:**")
                    st.write(f"☀️ Sunny days: {sunny}")
                    st.write(f"☁️ Cloudy days: {cloudy}")
                    st.write(f"🌧️ Rainy days: {rainy}")
                    
                except Exception:
                    st.error("Something went wrong. Try again.")

            else:
                st.error('Cannot find weather for this city. Check spelling.')

        else:
            st.warning('Please type your city name.')

# Watering advice
elif choice == 'When should I water?':
    st.header("💧 Watering Help")
    
    st.write("**Where are you?**")
    
    location_type = st.radio(
        "",
        ("Type my city", "Find me automatically")
    )

    if location_type == "Type my city":
        city = st.text_input('City name:')
    else:
        city = get_user_city()
        if city:
            st.success(f"Found you in: {city}")
        else:
            st.error("Cannot find you. Please type your city.")
            city = st.text_input('City name:')

    if st.button('Tell Me When to Water', type="primary"):
        if city:
            st.info('Checking weather now...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                st.write(f"**Right now in {city}:**")
                st.write(f"Temperature: {temp}°C")
                st.write(f"Humidity: {humidity}%")

                try:
                    water_advice = irrigation_advice(temp, humidity)
                    
                    st.success("Here's what to do:")
                    
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 30px; border-radius: 15px; text-align: center;">
                        <h1 style="color: #1976d2; margin: 0; font-size: 2em;">💦</h1>
                        <h2 style="color: #1976d2; margin: 10px 0;">{water_advice}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                        
                except Exception:
                    st.error("Cannot get watering advice. Try again.")
            else:
                st.error('Cannot find weather for this city.')
        else:
            st.warning('Please enter your city.')

# Default message
if choice == 'Select':
    st.info("👆 Choose what you need help with")

st.markdown("---")
st.write("🌾 Making farming simple for everyone")
