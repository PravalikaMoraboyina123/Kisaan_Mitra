"""
Weather module - Provides weather forecasts and AI-powered farming advice based on weather conditions.
"""

import sys
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_response
from config import WEATHER_API_BASE, SUPPORTED_LANGUAGES

# Mock weather data for when API is not available
MOCK_WEATHER_DATA = {
    "list": [
        {
            "dt": int(datetime.now().timestamp()),
            "main": {"temp": 28.5, "feels_like": 30.2, "humidity": 65},
            "weather": [{"main": "Clear", "icon": "01d"}],
            "wind": {"speed": 3.5, "deg": 180}
        },
        {
            "dt": int((datetime.now() + timedelta(days=1)).timestamp()),
            "main": {"temp": 29.0, "feels_like": 31.0, "humidity": 60},
            "weather": [{"main": "Partly Cloudy", "icon": "02d"}],
            "wind": {"speed": 4.0, "deg": 190}
        },
        {
            "dt": int((datetime.now() + timedelta(days=2)).timestamp()),
            "main": {"temp": 27.5, "feels_like": 29.5, "humidity": 70},
            "weather": [{"main": "Clouds", "icon": "03d"}],
            "wind": {"speed": 3.0, "deg": 200}
        },
        {
            "dt": int((datetime.now() + timedelta(days=3)).timestamp()),
            "main": {"temp": 26.0, "feels_like": 28.0, "humidity": 75},
            "weather": [{"main": "Light Rain", "icon": "10d"}],
            "wind": {"speed": 5.0, "deg": 210}
        },
        {
            "dt": int((datetime.now() + timedelta(days=4)).timestamp()),
            "main": {"temp": 25.5, "feels_like": 27.5, "humidity": 80},
            "weather": [{"main": "Moderate Rain", "icon": "10d"}],
            "wind": {"speed": 6.0, "deg": 220}
        },
        {
            "dt": int((datetime.now() + timedelta(days=5)).timestamp()),
            "main": {"temp": 26.5, "feels_like": 28.5, "humidity": 75},
            "weather": [{"main": "Light Rain", "icon": "10d"}],
            "wind": {"speed": 4.5, "deg": 200}
        },
        {
            "dt": int((datetime.now() + timedelta(days=6)).timestamp()),
            "main": {"temp": 28.0, "feels_like": 30.0, "humidity": 68},
            "weather": [{"main": "Partly Cloudy", "icon": "02d"}],
            "wind": {"speed": 3.8, "deg": 180}
        }
    ],
    "city": {"name": "Sample City", "country": "IN"}
}

# Weather condition icons/emojis
WEATHER_ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Smoke": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌪️",
    "Fog": "🌫️",
    "Sand": "🌪️",
    "Ash": "🌋",
    "Squall": "💨",
    "Tornado": "🌪️"
}

def get_weather(district: str, api_key: str = "") -> dict:
    """
    Get 7-day weather forecast for a district.
    Falls back to mock data if API key is not provided or API call fails.

    Args:
        district: District name
        api_key: OpenWeatherMap API key (optional)

    Returns:
        dict: Weather forecast data with 7-day list and city info
    """
    if not api_key:
        mock_data = {
            "list": MOCK_WEATHER_DATA["list"],
            "city": {"name": district, "country": "IN"}
        }
        return mock_data

    try:
        url = f"{WEATHER_API_BASE}/forecast"
        params = {
            "q": f"{district},IN",
            "appid": api_key,
            "units": "metric",
            "cnt": 56
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        daily_forecasts = {}
        for item in data.get("list", []):
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date not in daily_forecasts:
                daily_forecasts[date] = item

        simplified_list = []
        for date, forecast in daily_forecasts.items():
            simplified_list.append({
                "dt": forecast["dt"],
                "main": forecast["main"],
                "weather": forecast["weather"],
                "wind": forecast.get("wind", {})
            })

        return {
            "list": simplified_list[:7],
            "city": data.get("city", {"name": district, "country": "IN"})
        }

    except requests.exceptions.RequestException:
        mock_data = {
            "list": MOCK_WEATHER_DATA["list"],
            "city": {"name": district, "country": "IN"}
        }
        return mock_data
    except Exception:
        mock_data = {
            "list": MOCK_WEATHER_DATA["list"],
            "city": {"name": district, "country": "IN"}
        }
        return mock_data


def get_weather_advice(crop: str, forecast: dict, lang: str = "en", settings: dict = None) -> str:
    """
    Get AI-generated farming advice based on weather forecast and crop stage.

    Args:
        crop: Crop name
        forecast: Weather forecast dictionary from get_weather()
        lang: Language code ("en", "hi", or "te")
        settings: AI provider settings dictionary

    Returns:
        str: AI-generated farming advice in the specified language
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}

    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    try:
        weather_summary = []
        for day in forecast.get("list", [])[:7]:
            date = datetime.fromtimestamp(day["dt"]).strftime("%d/%m")
            temp = day["main"].get("temp", "N/A")
            humidity = day["main"].get("humidity", "N/A")
            weather_main = day["weather"][0]["main"] if day.get("weather") else "Unknown"
            weather_summary.append(f"{date}: {weather_main}, {temp}°C, {humidity}% humidity")

        weather_text = "\n".join(weather_summary)

        if lang == "hi":
            prompt = f"""किसान सलाह दें:

फसल: {crop}
7-दिन का मौसम पूर्वानुमान:
{weather_text}

इस मौसम पूर्वानुमान के आधार पर, कृपया इस फसल के लिए विशेष खेती सलाह प्रदान करें।
सलाह में शामिल करें:
- सिंचाई प्रबंधन
- कीट और रोग प्रबंधन
- उर्वरक प्रबंधन
- किसी भी आगामी मौसम घटनाओं के लिए तैयारी

पूरा उत्तर हिंदी में दें।"""

        elif lang == "te":
            prompt = f"""రైతు సలహా ఇవ్వండి:

పంట: {crop}
7-రోజుల వాతావరణ అంచనా:
{weather_text}

ఈ వాతావరణ అంచనా ఆధారంగా, దయచేసి ఈ పంటకు ప్రత్యేక వ్యవసాయ సలహాలను అందించండి.
సలహాలలో ఇవి ఉండాలి:
- నీటిపారుదల నిర్వహణ
- తెగులు మరియు వ్యాధి నిర్వహణ
- ఎరువుల నిర్వహణ
- రాబోయే వాతావరణ సంఘటనలకు సిద్ధత

పూర్తి సమాధానం తెలుగులో ఇవ్వండి."""

        else:
            prompt = f"""Provide farming advice:

Crop: {crop}
7-day weather forecast:
{weather_text}

Based on this weather forecast, please provide specific farming advice for this crop.
Include advice on:
- Irrigation management
- Pest and disease management
- Fertilizer management
- Preparation for any upcoming weather events

Provide the complete response in English."""

        system_prompt = f"""You are an expert agricultural advisor. Provide practical, actionable farming advice based on weather conditions.
Respond entirely in {lang} language."""

        advice = get_response(prompt, system_prompt, settings)

        if advice.startswith("Error:"):
            return "Unable to generate weather-based advice at this time. Please try again later."

        return advice

    except Exception as e:
        return f"Error generating weather advice: {str(e)}"