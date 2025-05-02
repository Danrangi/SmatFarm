def irrigation_advice(temp, humidity, rainfall=None):
    if rainfall is not None:
        if rainfall > 50:
            return "🌧️ Very heavy rain. No irrigation needed for the next few days."
        elif 20 < rainfall <= 50:
            return "🌦️ Moderate rain. Minimal irrigation needed today."
        elif 5 < rainfall <= 20:
            return "🌧️ Light rain. Reduce watering by 50%."
        else:
            
            pass
            
    if temp > 32 and humidity < 40:
        return "🔥 High temp and low humidity. Water heavily (25 L/sq.m)."
    elif 25 <= temp <= 32:
        return "☀️ Moderate temp. Water moderately (15–20 L/sq.m)."
    elif temp < 25:
        return "❄️ Cool weather. Light watering (10 L/sq.m)."
    else:
        return "🔍 Not enough information. Please check inputs."
