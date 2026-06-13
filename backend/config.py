"""
Configuration file for Kisaan Mitra backend.
Contains all constants, API endpoints, and model configurations.
"""

# Supported languages for the application
SUPPORTED_LANGUAGES = ["en", "hi", "te"]

# Language names for display
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिंदी",
    "te": "తెలుగు"
}

# Ollama configuration for local AI inference
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODELS = ["llama3.2:1b", "gemma3:latest", "llama3", "mistral", "gemma2"]

# Cloud AI models available for BYOK (Bring Your Own Tokens)
CLOUD_MODELS = ["gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"]

# API key placeholders (never hardcode real keys)
# Note: Using Open-Meteo for weather (free, no API key needed)
# Note: Using Open-Meteo Geocoding for location lookup (free, no API key needed)
DATAGOV_API_KEY = ""      # Set via environment variable or user input

# External API base URLs
WEATHER_API_BASE = "https://api.open-meteo.com/v1"  # Free weather API (no key needed)
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"  # Free geocoding (no key needed)
MANDI_API_BASE = "https://api.data.gov.in/resource"

# Common crops with bilingual labels (English/Hindi)
COMMON_CROPS = [
    "Wheat/गेहूं",
    "Rice/धान",
    "Maize/मक्का",
    "Cotton/कपास",
    "Sugarcane/गन्ना",
    "Groundnut/मूंगफली",
    "Tomato/टमाटर",
    "Onion/प्याज"
]

# Indian states for scheme finder and mandi prices
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Government schemes database
GOVERNMENT_SCHEMES = {
    "PM-KISAN": {
        "description": "Pradhan Mantri Kisan Samman Nidhi",
        "benefit": "₹6,000 per year in 3 equal installments",
        "eligibility": "All landholding farmer families"
    },
    "PMFBY": {
        "description": "PM Fasal Bima Yojana",
        "benefit": "Crop insurance coverage",
        "eligibility": "All farmers growing notified crops"
    },
    "KCC": {
        "description": "Kisan Credit Card",
        "benefit": "Credit facility up to ₹3 lakhs at 4% interest",
        "eligibility": "All farmers with land or tenant farmers"
    }
}