"""
Weather page - Provides weather forecasts and AI-powered farming advice.
Uses Open-Meteo API (free, no API key required).
"""

import sys
import os
from datetime import datetime, timedelta
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from modules.weather import get_weather_advice
import streamlit as st

# Weather condition mapping to emojis
WEATHER_ICONS = {
    "clear": "☀️",
    "partly_cloudy": "⛅",
    "overcast": "☁️",
    "drizzle": "🌦️",
    "rain": "🌧️",
    "snow": "❄️",
    "thunderstorm": "⛈️",
}

# WMO Weather Code mapping
WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "☀️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌦️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "❄️"),
    73: ("Moderate snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌧️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "🌧️"),
    85: ("Slight snow showers", "❄️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with hail", "⛈️"),
}


def geocode_location(city_name: str) -> dict:
    """
    Geocode city name to latitude and longitude using Open-Meteo Geocoding API.
    
    Args:
        city_name: City or district name
    
    Returns:
        dict with lat, lng, name, or None if not found
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "name": result.get("name"),
                "country": result.get("country"),
                "admin1": result.get("admin1", "")
            }
        return None
    except Exception as e:
        return None


def get_forecast_from_openmeteo(latitude: float, longitude: float) -> dict:
    """
    Fetch weather forecast from Open-Meteo API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        dict with current weather and 7-day forecast
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,rain",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max",
            "temperature_unit": "celsius",
            "wind_speed_unit": "ms",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        return None


def show_weather(t, common_crops, settings):
    """
    Display the Weather Forecast page using Open-Meteo API.
    
    Args:
        t: Translation function
        common_crops: List of common crops from config
        settings: AI provider settings dictionary
    """
    st.title(t("weather_title"))
    st.write(t("weather_description"))
    
    # Create form for weather forecast
    with st.form("weather_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            district = st.text_input(
                t("weather_district_label"),
                placeholder=t("weather_district_placeholder")
            )
        
        with col2:
            crop = st.selectbox(
                t("weather_crop_label"),
                options=common_crops
            )
        
        submitted = st.form_submit_button(
            t("weather_submit"),
            use_container_width=True
        )
    
    if submitted:
        if not district:
            st.error(t("error_generic"))
        else:
            with st.spinner(t("loading")):
                try:
                    # Get current language from session state
                    lang = st.session_state.get("lang", "en")
                    
                    # Step 1: Geocode the location
                    location = geocode_location(district)
                    
                    if not location:
                        st.error(f"❌ Could not find location: **{district}**. Please try a different city/district name.")
                    else:
                        # Step 2: Fetch weather data
                        weather_data = get_forecast_from_openmeteo(
                            location["latitude"],
                            location["longitude"]
                        )
                        
                        if not weather_data:
                            st.error("Unable to fetch weather data. Please try again.")
                        else:
                            # Display location info
                            location_display = f"{location['name']}"
                            if location.get('admin1'):
                                location_display += f", {location['admin1']}"
                            st.info(f"📍 Weather for: **{location_display}**, India")
                            
                            # Extract current weather
                            current = weather_data.get("current", {})
                            current_temp = current.get("temperature_2m", "N/A")
                            current_humidity = current.get("relative_humidity_2m", "N/A")
                            current_wind = current.get("wind_speed_10m", "N/A")
                            current_rain = current.get("rain", 0)
                            weather_code = current.get("weather_code", 3)
                            weather_desc, weather_icon = WMO_CODES.get(weather_code, ("Unknown", "🌤️"))
                            
                            # Display current weather prominently
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("🌡️ Temperature", f"{current_temp}°C")
                            with col2:
                                st.metric("💧 Humidity", f"{current_humidity}%")
                            with col3:
                                st.metric("💨 Wind Speed", f"{current_wind} m/s")
                            with col4:
                                st.metric("🌧️ Rain", f"{current_rain} mm")
                            
                            # Display 7-day forecast
                            st.subheader(t("weather_forecast_title"))
                            
                            daily_data = weather_data.get("daily", {})
                            dates = daily_data.get("time", [])
                            temps_max = daily_data.get("temperature_2m_max", [])
                            temps_min = daily_data.get("temperature_2m_min", [])
                            precip = daily_data.get("precipitation_sum", [])
                            weather_codes = daily_data.get("weather_code", [])
                            winds = daily_data.get("wind_speed_10m_max", [])
                            
                            # Create columns for 7-day forecast cards
                            cols = st.columns(7)
                            
                            for i in range(min(7, len(dates))):
                                with cols[i]:
                                    date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
                                    date_str = date_obj.strftime("%d/%m")
                                    
                                    code = weather_codes[i] if i < len(weather_codes) else 3
                                    desc, icon = WMO_CODES.get(code, ("Unknown", "🌤️"))
                                    
                                    st.markdown(f"**{date_str}**")
                                    st.markdown(f"# {icon}")
                                    st.write(f"{temps_max[i]}°/{temps_min[i]}°C")
                                    st.caption(f"💧 {precip[i]} mm")
                            
                            # Display detailed forecast table
                            st.markdown("### 📊 Detailed 7-Day Forecast")
                            forecast_data = []
                            
                            for i in range(min(7, len(dates))):
                                date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
                                date_str = date_obj.strftime("%d/%m/%Y")
                                
                                code = weather_codes[i] if i < len(weather_codes) else 3
                                desc, icon = WMO_CODES.get(code, ("Unknown", "🌤️"))
                                
                                forecast_data.append({
                                    t("weather_date"): date_str,
                                    t("weather_condition"): f"{icon} {desc}",
                                    t("weather_temp"): f"↑{temps_max[i]}°C / ↓{temps_min[i]}°C",
                                    t("weather_humidity"): f"{precip[i]} mm",
                                    t("weather_wind"): f"{winds[i]:.1f} m/s"
                                })
                            
                            st.table(forecast_data)
                            
                            # Get AI weather advice
                            st.subheader(t("weather_advice_title"))
                            with st.spinner("Generating AI advice..."):
                                # Convert to format expected by get_weather_advice
                                forecast_dict = {
                                    "current": current,
                                    "daily": {
                                        "time": dates[:7],
                                        "temperature_2m_max": temps_max[:7],
                                        "temperature_2m_min": temps_min[:7],
                                        "precipitation_sum": precip[:7],
                                        "weather_code": weather_codes[:7]
                                    },
                                    "city": {"name": location["name"], "country": "IN"}
                                }
                                
                                advice = get_weather_advice(
                                    crop=crop,
                                    forecast=forecast_dict,
                                    lang=lang,
                                    settings=settings
                                )
                                
                                if advice and not advice.startswith("Error:"):
                                    st.info(advice)
                                else:
                                    st.warning("Unable to generate weather advice at this time.")
                    
                except Exception as e:
                    st.error(f"{t('error_generic')}: {str(e)}")
