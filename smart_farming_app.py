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
        print(f"Error detecting location: {e}")
        return None

def get_regional_alternatives(temp, humidity, rain_days):
    """Get alternative crop suggestions based on general farming knowledge"""
    alternatives = []
    
    # Hot and dry conditions
    if temp > 25 and humidity < 60 and rain_days < 10:
        alternatives = ["Millet", "Sorghum", "Sunflower", "Cotton"]
    
    # Hot and humid conditions
    elif temp > 25 and humidity >= 60:
        alternatives = ["Rice", "Sugarcane", "Banana", "Coconut"]
    
    # Moderate temperature with good rainfall
    elif 15 <= temp <= 25 and rain_days >= 10:
        alternatives = ["Wheat", "Barley", "Potato", "Cabbage"]
    
    # Cool and wet conditions
    elif temp < 15 and rain_days >= 15:
        alternatives = ["Oats", "Peas", "Lettuce", "Spinach"]
    
    # Moderate conditions
    else:
        alternatives = ["Maize", "Tomato", "Onion", "Carrot"]
    
    return alternatives

# Soil properties
soil_properties = {
    'Sand':  [20, 10, 15, 6.5],
    'Clay':  [50, 40, 45, 6.0],
    'Loam':  [60, 50, 50, 6.5],
    'Chalk': [25, 15, 20, 7.5],
    'Peat':  [80, 60, 70, 5.5],
    'Silt':  [55, 45, 40, 6.3]
}

# App configuration
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

                future_data = future_data.rename(columns={'temperature': 'temp'})
                future_data = future_data[['temp', 'humidity', 'month', 'day']]

                future_predictions = weather_model.predict(future_data)

                label_map = {0: 'clear', 1: 'clouds', 2: 'rain'}
                predicted_labels = [label_map[label] for label in future_predictions]

                future_data['predicted_weather'] = predicted_labels

                weather_counts = future_data['predicted_weather'].value_counts()
                
                # Enhanced weather display
                st.subheader('🌦️ Weather Forecast Summary:')
                col1, col2, col3 = st.columns(3)
                
                rain_days = weather_counts.get('rain', 0)
                clear_days = weather_counts.get('clear', 0)
                clouds_days = weather_counts.get('clouds', 0)
                
                with col1:
                    st.metric("☀️ Clear Days", clear_days)
                with col2:
                    st.metric("☁️ Cloudy Days", clouds_days)
                with col3:
                    st.metric("🌧️ Rainy Days", rain_days)

                # AI Crop Recommendation (Primary)
                avg_future_temp = np.mean(future_data['temp'])
                avg_future_humidity = np.mean(future_data['humidity'])
                estimated_rainfall = rain_days * 8  # Better rainfall estimation

                features = np.array([[N, P, K, avg_future_temp, avg_future_humidity, ph, estimated_rainfall]])
                
                try:
                    ai_crop_prediction = crop_model.predict(features)[0]

                    st.markdown("---")
                    st.markdown("### 🤖 AI Recommendation")
                    st.markdown(f"""
                    <div style="background-color: #e8f5e8; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #4CAF50; margin: 20px 0;">
                        <h1 style="color: #2e7d32; margin: 0; font-size: 2.5em;">🌾</h1>
                        <h1 style="color: #2e7d32; margin: 10px 0; font-size: 2em;">{ai_crop_prediction}</h1>
                        <h4 style="color: #388e3c; margin: 0;">AI's top recommendation for your conditions</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Alternative Suggestions (Secondary)
                    alternatives = get_regional_alternatives(avg_future_temp, avg_future_humidity, rain_days)
                    
                    st.markdown("### 🌍 Additional Options for Your Climate")
                    st.markdown(f"""
                    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border: 1px solid #87CEEB; margin: 10px 0;">
                        <p style="color: #4682B4; margin: 0; font-size: 0.9em; text-align: center;">
                            <em>Based on general farming knowledge for similar weather conditions</em>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display alternatives in a grid
                    cols = st.columns(2)
                    for i, crop in enumerate(alternatives):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 5px 0; text-align: center; border: 1px solid #dee2e6;">
                                <h4 style="color: #495057; margin: 0;">🌱 {crop}</h4>
                            </div>
                            """, unsafe_allow_html=True)

                    # Analysis Details
                    st.markdown("---")
                    st.markdown("### 📊 Analysis Details")
                    
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Soil Analysis:**")
                        st.write(f"• Soil Type: {soil_type}")
                        st.write(f"• Nitrogen (N): {N} kg/ha")
                        st.write(f"• Phosphorus (P): {P} kg/ha")
                        st.write(f"• Potassium (K): {K} kg/ha")
                        st.write(f"• pH Level: {ph}")
                    
                    with detail_col2:
                        st.markdown("**Weather Analysis:**")
                        st.write(f"• Avg Temperature: {avg_future_temp:.1f}°C")
                        st.write(f"• Avg Humidity: {avg_future_humidity:.1f}%")
                        st.write(f"• Expected Rainfall: {estimated_rainfall}mm")
                        st.write(f"• Location: {city}")

                except Exception as e:
                    st.error(f"❌ Error in AI prediction: {str(e)}")

            else:
                st.error('❌ Could not fetch weather. Check city name.')

        else:
            st.warning('⚠️ Please enter your city!')

# Irrigation Advice Section
elif option == 'Get Irrigation Advice':
    st.header("💧 Get Irrigation Advice")

    location_choice = st.radio(
        "How would you like to provide your location?",
        ("Enter City Manually", "Use My Current Location")
    )

    if location_choice == "Enter City Manually":
        city = st.text_input('Enter City Name:')
    else:
        city = get_user_city()
        if city:
            st.success(f"Detected City: {city}")
        else:
            st.error("❌ Could not detect your location. Please enter manually.")

    if st.button('Get Irrigation Advice'):
        if city:
            st.success('Fetching real-time weather...')
            temp, humidity = get_current_weather(city)

            if temp is not None:
                # Enhanced weather display
                st.markdown("### 🌡️ Current Weather Conditions")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Temperature", f"{temp}°C")
                with col2:
                    st.metric("Humidity", f"{humidity}%")

                try:
                    irrigation = irrigation_advice(temp, humidity)
                    
                    st.markdown("---")
                    st.markdown("### 💦 Irrigation Recommendation")
                    
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #2196F3; margin: 20px 0;">
                        <h1 style="color: #1976d2; margin: 0; font-size: 2em;">💧</h1>
                        <h2 style="color: #1976d2; margin: 10px 0;">{irrigation}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Additional context based on conditions
                    st.markdown("### 📋 Additional Tips")
                    if temp > 30:
                        st.warning("🌡️ **High Temperature Alert**: Monitor soil moisture closely and consider watering during cooler parts of the day")
                    if humidity < 40:
                        st.warning("💨 **Low Humidity**: Plants may need extra water due to increased evaporation")
                    elif humidity > 80:
                        st.info("💧 **High Humidity**: Reduce watering frequency to prevent fungal diseases")
                    
                    if 20 <= temp <= 25 and 50 <= humidity <= 70:
                        st.success("🌿 **Ideal Conditions**: Perfect weather for most crops!")

                except Exception as e:
                    st.error(f"❌ Error getting irrigation advice: {str(e)}")
            else:
                st.error('❌ Could not fetch weather. Check city name.')
        else:
            st.warning('⚠️ Please provide a city or allow location detection.')

# Footer
st.markdown("---")
st.markdown("🌾 **Smart Farming Assistant** - Combining AI intelligence with agricultural expertise")
