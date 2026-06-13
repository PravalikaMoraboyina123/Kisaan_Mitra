"""
Mandi Prices module - Provides real-time mandi prices and AI-powered selling advice.
"""

import sys
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_response
from config import MANDI_API_BASE, SUPPORTED_LANGUAGES

# Mock mandi price data for when API is not available
MOCK_MANDI_PRICES = [
    {"mandi_name": "Delhi Azadpur", "price": 1850, "unit": "per quintal", "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d")},
    {"mandi_name": "Mumbai Vashi", "price": 1900, "unit": "per quintal", "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
    {"mandi_name": "Kolkata Sealdah", "price": 1800, "unit": "per quintal", "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")},
    {"mandi_name": "Chennai Koyambedu", "price": 1950, "unit": "per quintal", "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")},
    {"mandi_name": "Bangalore Yeshwanthpur", "price": 1880, "unit": "per quintal", "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")},
]

# Commodity name mappings (English to Hindi for better API search)
COMMODITY_NAMES = {
    "Wheat": "गेहूं",
    "Rice": "धान",
    "Maize": "मक्का",
    "Cotton": "कपास",
    "Sugarcane": "गन्ना",
    "Groundnut": "मूंगफली",
    "Tomato": "टमाटर",
    "Onion": "प्याज"
}

def get_mandi_prices(commodity: str, state: str, api_key: str = "") -> List[Dict]:
    """
    Get current mandi prices for a commodity in a specific state.
    Falls back to mock data if API key is not provided or API call fails.
    
    Args:
        commodity: Commodity name (e.g., "Wheat", "Rice")
        state: State name
        api_key: data.gov.in API key (optional)
    
    Returns:
        List[Dict]: List of price records with mandi_name, price, unit, date
    """
    # Extract English name if commodity contains Hindi translation
    commodity_en = commodity.split("/")[0].strip() if "/" in commodity else commodity
    
    if not api_key:
        # Return mock data with variations based on commodity and state
        mock_data = []
        base_price = _get_base_price(commodity_en)
        
        mandis = _get_mandis_for_state(state)
        for i, mandi in enumerate(mandis[:5]):
            mock_data.append({
                "mandi_name": mandi,
                "price": base_price + (i * 50) - 100,
                "unit": "per quintal",
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "commodity": commodity_en
            })
        
        return mock_data
    
    try:
        # Try to get real data from data.gov.in API
        # Note: This is a simplified example - actual API may require specific resource IDs
        url = f"{MANDI_API_BASE}/resource-url"
        params = {
            "api-key": api_key,
            "commodity": commodity_en,
            "state": state,
            "limit": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the response (structure depends on actual API)
        prices = []
        for record in data.get("records", []):
            prices.append({
                "mandi_name": record.get("market", "Unknown"),
                "price": record.get("price", 0),
                "unit": record.get("unit", "per quintal"),
                "date": record.get("date", datetime.now().strftime("%Y-%m-%d")),
                "commodity": record.get("commodity", commodity_en)
            })
        
        return prices if prices else MOCK_MANDI_PRICES
        
    except requests.exceptions.RequestException as e:
        # Return mock data on API failure
        return _generate_mock_prices(commodity_en, state)
    except Exception as e:
        return _generate_mock_prices(commodity_en, state)


def _get_base_price(commodity: str) -> int:
    """Get base price for common commodities (in ₹ per quintal)."""
    base_prices = {
        "Wheat": 2200,
        "Rice": 3000,
        "Maize": 1800,
        "Cotton": 6000,
        "Sugarcane": 300,
        "Groundnut": 5000,
        "Tomato": 2000,
        "Onion": 1800
    }
    return base_prices.get(commodity, 2000)


def _get_mandis_for_state(state: str) -> List[str]:
    """Get major mandis for a given state."""
    mandis_by_state = {
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
        "Haryana": ["Karnal", "Hisar", "Rohtak", "Panipat", "Ambala"],
        "Uttar Pradesh": ["Meerut", "Kanpur", "Lucknow", "Agra", "Varanasi"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Udaipur"],
        "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
        "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam"],
    }
    
    # Find closest match
    for state_key, mandis in mandis_by_state.items():
        if state.lower() in state_key.lower() or state_key.lower() in state.lower():
            return [f"{state_key} {mandi}" for mandi in mandis]
    
    # Default mandis if state not found
    return [f"Major Mandi {i+1}" for i in range(5)]


def _generate_mock_prices(commodity: str, state: str) -> List[Dict]:
    """Generate mock price data based on commodity and state."""
    base_price = _get_base_price(commodity)
    mandis = _get_mandis_for_state(state)
    
    prices = []
    for i, mandi in enumerate(mandis[:5]):
        # Add some price variation
        price_variation = (i * 30) - 60
        prices.append({
            "mandi_name": mandi,
            "price": base_price + price_variation,
            "unit": "per quintal",
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "commodity": commodity
        })
    
    return prices


def get_price_advice(commodity: str, prices: List[Dict], lang: str = "en", settings: dict = None) -> str:
    """
    Get AI-generated advice on whether to sell, hold, or transport based on price trends.
    
    Args:
        commodity: Commodity name
        prices: List of price records from get_mandi_prices()
        lang: Language code ("en", "hi", or "te")
        settings: AI provider settings dictionary
    
    Returns:
        str: AI-generated advice in the specified language
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}
    
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    
    try:
        # Analyze price trends
        if not prices:
            return "No price data available for analysis."
        
        # Extract prices and calculate trends
        price_values = [p["price"] for p in prices]
        avg_price = sum(price_values) / len(price_values)
        min_price = min(price_values)
        max_price = max(price_values)
        
        # Determine trend (simple linear regression)
        if len(price_values) >= 2:
            trend = "stable"
            if price_values[-1] > price_values[0] * 1.05:
                trend = "increasing"
            elif price_values[-1] < price_values[0] * 0.95:
                trend = "decreasing"
        else:
            trend = "insufficient data"
        
        # Create price summary
        price_summary = "\n".join([
            f"- {p['mandi_name']}: ₹{p['price']}/quintal ({p['date']})"
            for p in prices[:5]
        ])
        
        # Create prompt based on language
        if lang == "hi":
            prompt = f"""मंडी मूल्य सलाह विश्लेषण:

फसल: {commodity}
मूल्य प्रवृत्ति: {trend}
औसत मूल्य: ₹{avg_price:.0f}/क्विंटल
न्यूनतम मूल्य: ₹{min_price}/क्विंटल
अधिकतम मूल्य: ₹{max_price}/क्विंटल

मंडी मूल्य विवरण:
{price_summary}

किसानों के लिए सलाह प्रदान करें:
1. क्या उन्हें अभी बेचना चाहिए या रोक कर रखना चाहिए?
2. क्या उन्हें किसी अन्य मंडी में परिवहन करना चाहिए?
3. मूल्य प्रवृत्ति के आधार पर भविष्य की रणनीति

पूरा उत्तर हिंदी में दें।"""
        
        elif lang == "te":
            prompt = f"""మండి ధరల సలహా విశ్లేషణ:

పంట: {commodity}
ధర ధోరణి: {trend}
సగటు ధర: ₹{avg_price:.0f}/క్వింటాల్
కనిష్ట ధర: ₹{min_price}/క్వింటాల్
గరిష్ట ధర: ₹{max_price}/క్వింటాల్

మండి ధరల వివరాలు:
{price_summary}

రైతులకు సలహాలు ఇవ్వండి:
1. వారు ఇప్పుడు అమ్మాలా లేదా నిల్వ ఉంచుకోవాలా?
2. వారు వేరే మండికి తరలించాలా?
3. ధర ధోరణి ఆధారంగా భవిష్యత్ వ్యూహం

పూర్తి సమాధానం తెలుగులో ఇవ్వండి."""
        
        else:
            prompt = f"""Mandi Price Advice Analysis:

Crop: {commodity}
Price Trend: {trend}
Average Price: ₹{avg_price:.0f}/quintal
Lowest Price: ₹{min_price}/quintal
Highest Price: ₹{max_price}/quintal

Mandi Price Details:
{price_summary}

Provide advice for farmers:
1. Should they sell now or hold?
2. Should they transport to another mandi?
3. Future strategy based on price trends

Provide the complete response in English.""",
        
        system_prompt = f"""You are an agricultural market expert. Provide practical advice on crop selling strategies based on current mandi prices and trends. 
        Consider transportation costs, price differentials, and market timing. 
        Respond entirely in {lang} language."""
        
        advice = get_response(prompt, system_prompt, settings)
        
        if advice.startswith("Error:"):
            return "Unable to generate price advice at this time. Please try again later."
        
        return advice
        
    except Exception as e:
        return f"Error generating price advice: {str(e)}"