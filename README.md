🌾 Smart Farming Assistant 🚜

A smart web application built with **Streamlit** that helps farmers make informed decisions by recommending the best crops to plant based on their **soil type and location's weather, and also gives irrigation advice using real-time weather data 🌦️💧.


Features

Crop Recommendation  
- Uses AI to recommend the best crop to plant  
- Based on soil nutrients (N, P, K), pH, humidity, temperature, and rainfall  
- Simulates future weather for 30 days using real-time conditions  
- Offers both rule-based and AI-powered suggestions  

Irrigation Advice
- Gives smart daily water usage advice  
- Based on real-time temperature, humidity, and rainfall  
- Supports auto-location detection or manual city input  

User-Friendly Interface  
- Built with Streamlit — fast, clean, and mobile-friendly  
- Automatically fetches weather from OpenWeatherMap API  
- Runs in the browser, no installation required


How It Works

1. Crop Recommendation
   - User selects soil type and enters a city name.
   - App fetches current weather → simulates 30 days → feeds average into trained model.
   - Displays AI-recommended crop and rule-based fallback suggestion.

2. Irrigation Advice
   - User enters city or uses auto-detection.
   - Real-time weather fetched via OpenWeatherMap API.
   - App advises on how much water is needed based on weather conditions.

Technologies Used

- Python
- Streamlit
- Scikit-learn
- Pandas & NumPy
- OpenWeatherMap API
- Joblib (for model serialization)


