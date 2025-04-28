# smart_farming_app.py

# 1. Import Libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib

from irrigation_logic import irrigation_advice  # Your irrigation function

# 2. Load trained models
crop_model = joblib.load('crop_recommendation_model.pkl')
weather_model = joblib.load('weather_prediction_model.pkl')

# 3. Hardcoded API Key and Endpoint
API_KEY = "a54341456a66edadfce567ab9e85f0e8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# 4. Function to get real-time weather from OpenWeatherMap
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

# 5. Soil properties mapping
soil_properties = {
    'Sand':  [20, 10, 15, 6.5],
    'Clay':  [50, 40, 45, 6.0],
    'Loam':  [60, 50, 50, 6.5],
    'Chalk': [25, 15, 20, 7.5],
    'Peat':  [80, 60, 70, 5.5],
    'Silt':  [55, 45, 40, 6.3]
}

# 6. Streamlit App Layout
st.title("🌾 Smart Farming Assistant")
st.write("Welcome! Get Crop Recommendation or Irrigation Advice based on your location and soil type.")

# 7. Two Main Options
option = st.selectbox(
    'What would you like to do?',
    ('Select an option', 'Get Crop Recommendation', 'Get Irrigation Advice')
)

# 🧠 Based on the option chosen
if option == 'Get Crop Recommendation':
    st.header("🌱 Get Crop Recommendation")

    soil_type = st.selectbox('Select Soil Type:', list(soil_properties.keys()))
    city = st.text_input('Enter City Name:')

    if st.button('Recommend Crop'):
        if city:
            st.success('Fetching real-time weather...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                st.write(f"🌡️ Current Temperature: {temp} °C")
                st.write(f"💧 Current Humidity: {humidity} %")

                N, P, K, ph = soil_properties.get(soil_type)

                # Predict 30 days of future weather
                st.success('Predicting next 30 days weather...')

                future_days = list(range(1, 31))
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
                st.subheader('🌦️ Weather Forecast Summary:')
                st.dataframe(weather_counts)

                rain_days = weather_counts.get('rain', 0)
                clear_days = weather_counts.get('clear', 0)
                clouds_days = weather_counts.get('clouds', 0)

                # Simple Crop Suggestion Rule
                if rain_days >= 15:
                    crop_recommendation = "🌾 Suggest planting Rice, Leafy Vegetables"
                elif clouds_days >= 15:
                    crop_recommendation = "🌽 Suggest planting Maize, Tomatoes"
                else:
                    crop_recommendation = "🍠 Suggest planting Millet, Sorghum (dry-tolerant crops)"

                st.success(crop_recommendation)

                # Advanced Crop Recommendation (using AI model)
                avg_future_temp = np.mean(future_data['temperature'])
                avg_future_humidity = np.mean(future_data['humidity'])
                avg_rainfall = 100  # Assume rainfall if not provided

                features = np.array([[N, P, K, avg_future_temp, avg_future_humidity, ph, avg_rainfall]])
                ai_crop_prediction = crop_model.predict(features)[0]

                st.subheader("🌱 AI Recommended Best Crop:")
                st.success(f"👉 You should plant: {ai_crop_prediction}")

            else:
                st.error('❌ Could not fetch weather. Check city name.')

        else:
            st.warning('⚠️ Please enter your city!')

elif option == 'Get Irrigation Advice':
    st.header("💧 Get Irrigation Advice")

    city = st.text_input('Enter City Name:')

    if st.button('Get Advice'):
        if city:
            st.success('Fetching real-time weather...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                st.write(f"🌡️ Current Temperature: {temp} °C")
                st.write(f"💧 Current Humidity: {humidity} %")

                irrigation = irrigation_advice(temp, humidity)
                st.success(f"💦 Irrigation Advice: {irrigation}")
            else:
                st.error('❌ Could not fetch weather. Check city name.')

        else:
            st.warning('⚠️ Please enter your city!')
