# smart_farming_app.py

# 1. Import Libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib

from irrigation_logic import irrigation_advice  # Import your rule-based irrigation function

# 2. Load the trained models
crop_model = joblib.load('crop_recommendation_model.pkl')
weather_model = joblib.load('weather_prediction_model.pkl')

# 3. Function to get real-time weather from OpenWeatherMap API
def get_current_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return temp, humidity
    else:
        return None, None

# 4. Soil properties mapping
soil_properties = {
    'Sand':  [20, 10, 15, 6.5],
    'Clay':  [50, 40, 45, 6.0],
    'Loam':  [60, 50, 50, 6.5],
    'Chalk': [25, 15, 20, 7.5],
    'Peat':  [80, 60, 70, 5.5],
    'Silt':  [55, 45, 40, 6.3]
}

# 5. Streamlit App Layout
st.title("🌾 Smart Farming Assistant")
st.write("Welcome! Get Crop Recommendation, Future Weather Forecast, and Irrigation Advice.")

# Select Soil Type
st.header("Select Soil Type")
soil_type = st.selectbox('Choose your soil type:', ['Sand', 'Clay', 'Loam', 'Chalk', 'Peat', 'Silt'])

# City and API Key Input
st.header("Enter Location Info")
city = st.text_input('City Name')
api_key = st.text_input('OpenWeatherMap API Key', type='password')

# Predict Button
if st.button('Predict'):
    if city and api_key:
        st.success('Fetching real-time weather...')
        temp, humidity = get_current_weather(city, api_key)
        
        if temp is not None:
            st.write(f"🌡️ Current Temperature: {temp} °C")
            st.write(f"💧 Current Humidity: {humidity} %")

            # Irrigation Advice
            irrigation = irrigation_advice(temp, humidity)
            st.info(f"💦 Irrigation Advice: {irrigation}")

            # Soil properties
            N, P, K, ph = soil_properties.get(soil_type)

            # Future Weather Prediction
            st.success('Predicting future weather...')
            
            future_days = list(range(1, 31))  # Predict for next 30 days
            future_month = pd.Timestamp.now().month

            avg_temp = temp
            avg_humidity = humidity

            future_data = pd.DataFrame({
                'temperature': np.random.normal(loc=avg_temp, scale=2, size=30),
                'humidity': np.random.normal(loc=avg_humidity, scale=5, size=30),
                'month': [future_month]*30,
                'day': future_days
            })

            future_predictions = weather_model.predict(future_data)

            label_map = {0: 'clear', 1: 'clouds', 2: 'rain'}
            predicted_labels = [label_map[label] for label in future_predictions]

            future_data['predicted_weather'] = predicted_labels

            weather_counts = future_data['predicted_weather'].value_counts()
            st.subheader('🌦️ Forecast for the Next Month:')
            st.dataframe(weather_counts)

            rain_days = weather_counts.get('rain', 0)
            clear_days = weather_counts.get('clear', 0)
            clouds_days = weather_counts.get('clouds', 0)

            # Simple Rule-Based Crop Suggestion
            if rain_days >= 15:
                crop_recommendation = "🌾 Based on weather: Suggest Rice, Leafy Vegetables"
            elif clouds_days >= 15:
                crop_recommendation = "🌽 Based on weather: Suggest Maize, Tomatoes"
            else:
                crop_recommendation = "🍠 Based on weather: Suggest Millet, Sorghum (dry-season crops)"

            st.success(crop_recommendation)

            # Advanced AI Crop Recommendation
            avg_future_temp = np.mean(future_data['temperature'])
            avg_future_humidity = np.mean(future_data['humidity'])
            avg_rainfall = 100  # Assume average rainfall if missing

            features = np.array([[N, P, K, avg_future_temp, avg_future_humidity, ph, avg_rainfall]])
            ai_crop_prediction = crop_model.predict(features)[0]

            st.subheader("🌱 AI Recommended Crop Based on Soil + Weather:")
            st.success(f"👉 You should plant: {ai_crop_prediction}")

        else:
            st.error('❌ Could not fetch weather. Please check your City name and API key.')
    else:
        st.warning('⚠️ Please enter both your City and API key.')
