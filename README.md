# SmartFarm 🌾🚜

A web app that helps farmers decide what to grow and when to water. Uses real weather data and AI to give practical advice for your farm.

## What This Does

### Crop Recommendation
Pick a crop that matches your soil and weather. The app analyzes your soil nutrients (N, P, K), pH levels, and local weather patterns to suggest the best crop for your conditions. It pulls actual weather forecasts and predicts conditions 30 days out to make a smarter recommendation.

### Irrigation Advice  
Get daily watering suggestions based on current weather. The app checks temperature, humidity, and rainfall to tell you how much water your crops actually need—avoiding both dry fields and wasted water.

### Keeps It Simple
Everything runs in your browser. Just enter your location or let it detect where you are. No installation headaches, no complicated setup.

## How It Works

**For Crop Recommendations:**
1. Tell us your soil type and where you farm
2. We fetch real weather data for your area
3. The model predicts what the next 30 days will look like
4. You get back the best crop for those conditions

**For Watering:**
1. Enter your city (or we'll find it automatically)
2. Check current weather conditions
3. Get a water recommendation for today

## Tech Stack

- **Python** — the whole thing runs on Python
- **Streamlit** — keeps the UI fast and clean
- **Scikit-learn** — our ML models for predictions
- **Pandas & NumPy** — data handling and analysis
- **OpenWeatherMap API** — real-time weather data
- **Joblib** — saves and loads trained models

## Getting Started

### What You Need
- Python 3.8+
- An API key from OpenWeatherMap (free tier works)

### Setup

1. Clone the repo:
```bash
git clone https://github.com/Danrangi/SmatFarm.git
cd SmatFarm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your OpenWeatherMap API key (set it as an environment variable or in the app)

4. Run it:
```bash
streamlit run smart_farming_app.py
```

The app opens in your browser at `http://localhost:8501`

## What's In Here

- `smart_farming_app.py` — the main app you actually use
- `crop_recommendation_model.ipynb` — how we trained the crop model
- `weather_prediction_model.ipynb` — how we built the weather forecasting
- `irrigation_logic.py` — the watering recommendation logic
- `.pkl` files — trained models (already ready to go)
- `Crop_recommendation.csv` — the crop data we learned from
- `nigeria_cities_weather_data.csv` — historical weather patterns

## The Models

Both models were trained on real agricultural and weather data. The crop model learns from soil properties and historical growing patterns. The weather model uses past conditions to predict what's coming.

## Current Limitations

- Focused on Nigerian geography right now (based on our training data)
- Works best with known crops and soil types
- Relies on OpenWeatherMap data accuracy

## Future Ideas

- Add more regions beyond Nigeria
- Mobile app (Flutter app started, contributions welcome)
- Better soil data integration
- Pest and disease predictions

## License

MIT License — use it however you want

## Questions?

Open an issue if something's broken or unclear. Contributions are welcome.

---

Built by farmers who wanted better tools. Feel free to fork, improve, and share.
