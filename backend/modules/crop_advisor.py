"""
Crop Advisor module - AI-powered agricultural recommendations with Claude API fallback.
Features: Multi-language support, hybrid Ollama+Claude architecture, agronomy date validation.
"""

import sys
import os
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_response, get_claude_response
from config import SUPPORTED_LANGUAGES

# Sowing season guidelines for Indian crops (Month ranges: 1-12)
CROP_SEASONS = {
    "Wheat/गेहूं": {
        "start_month": 10, "end_month": 12,
        "warnings": {
            "en": "Wheat is typically sown in October-December. June is off-season.",
            "hi": "गेहूं आमतौर पर अक्टूबर-दिसंबर में बोया जाता है। जून ऑफ-सीजन है।",
            "te": "గెలుసు సాధారణంగా అక్టోబర్-డిసెంబర్‌లో విత్తనం చేస్తారు. జూన్ ఆఫ్-సీజన్."
        }
    },
    "Rice/धान": {
        "start_month": 6, "end_month": 8,
        "warnings": {
            "en": "Rice is typically sown in June-August. December is off-season.",
            "hi": "चावल आमतौर पर जून-अगस्त में बोया जाता है। दिसंबर ऑफ-सीजन है।",
            "te": "ధానం సాధారణంగా జూన్-ఆగస్టులో విత్తనం చేస్తారు. డిసెంబర్ ఆఫ్-సీజన్."
        }
    },
    "Maize/मक्का": {
        "start_month": 4, "end_month": 7,
        "warnings": {
            "en": "Maize is typically sown in April-July. October-December is off-season.",
            "hi": "मक्का आमतौर पर अप्रैल-जुलाई में बोया जाता है। अक्टूबर-दिसंबर ऑफ-सीजन है।",
            "te": "మక్క సాధారణంగా ఏప్రిల్-జూలై నడుమలో విత్తనం చేస్తారు. అక్టోబర్-డిసెంబర్ ఆఫ్-సీజన్."
        }
    },
    "Cotton/कपास": {
        "start_month": 5, "end_month": 7,
        "warnings": {
            "en": "Cotton is typically sown in May-July. December-April is off-season.",
            "hi": "कपास आमतौर पर मई-जुलाई में बोया जाता है। दिसंबर-अप्रैल ऑफ-सीजन है।",
            "te": "కటన్ సాధారణంగా మే-జూలై నడుమలో విత్తనం చేస్తారు. డిసెంబర్-ఏప్రిల్ ఆఫ్-సీజన్."
        }
    },
    "Sugarcane/गन्ना": {
        "start_month": 9, "end_month": 12,
        "warnings": {
            "en": "Sugarcane is typically sown in September-December.",
            "hi": "गन्ना आमतौर पर सितंबर-दिसंबर में बोया जाता है।",
            "te": "చెరకు సాధారణంగా సెప్టెంబర్-డిసెంబర్‌లో విత్తనం చేస్తారు."
        }
    },
    "Groundnut/मूंगफली": {
        "start_month": 5, "end_month": 7,
        "warnings": {
            "en": "Groundnut is typically sown in May-July.",
            "hi": "मूंगफली आमतौर पर मई-जुलाई में बोई जाती है।",
            "te": "వేరుశనగ సాధారణంగా మే-జూలై నడుమలో విత్తనం చేస్తారు."
        }
    },
    "Tomato/टमाटर": {
        "start_month": 1, "end_month": 12,
        "warnings": {
            "en": "Tomato can be grown year-round with season adjustment.",
            "hi": "टमाटर मौसम के समायोजन के साथ पूरे वर्ष उगाया जा सकता है।",
            "te": "టొమాటో సీజన్ సమయోజనం ద్వారా సమయం అంతా పెరుగుతుంది."
        }
    },
    "Onion/प्याज": {
        "start_month": 6, "end_month": 9,
        "warnings": {
            "en": "Onion is typically sown in June-September.",
            "hi": "प्याज आमतौर पर जून-सितंबर में बोया जाता है।",
            "te": "ఉల్లిపాయ సాధారణంగా జూన్-సెప్టెంబర్‌లో విత్తనం చేస్తారు."
        }
    },
}

# Language-specific system prompts
SYSTEM_PROMPTS = {
    "en": """RESPOND ONLY IN ENGLISH.

You are an expert agricultural advisor helping Indian farmers with crop-specific guidance.

CRITICAL INSTRUCTIONS:
- ALL responses MUST be in English only
- Generate ONLY valid JSON with exactly these 5 keys: seasonal_plan, fertilizer_schedule, pest_watch, harvest_window, tips
- Make responses SPECIFIC to the crop, location, and sowing date provided
- Include crop name explicitly in every section
- Reference actual NPK ratios, planting depths, and spacing for this specific crop
- Mention realistic maturity days and harvest timeframe
- Provide region-appropriate irrigation and pest management advice
- Keep content practical and farmer-friendly
- Do NOT mix languages. Use only English.

RESPOND ONLY with JSON (no markdown, no code blocks):
{
  "seasonal_plan": "Specific field preparation, planting depth, and spacing for this crop",
  "fertilizer_schedule": "NPK ratio and application schedule specific to this crop",
  "pest_watch": "Common pests and diseases for this specific crop",
  "harvest_window": "Expected maturity and harvest time based on sowing date",
  "tips": "Irrigation needs and management tips specific to this crop"
}""",

    "hi": """केवल हिंदी में जवाब दें। कोई अंग्रेजी नहीं।

आप भारतीय किसानों को फसल-विशिष्ट मार्गदर्शन प्रदान करने वाले कृषि विशेषज्ञ हैं।

महत्वपूर्ण निर्देश:
- सभी प्रतिक्रिया केवल हिंदी में होनी चाहिए
- केवल वैध JSON बनाएं जिसमें ये 5 कुंजियां हों: seasonal_plan, fertilizer_schedule, pest_watch, harvest_window, tips
- प्रतिक्रिया दी गई फसल, स्थान और बुवाई की तारीख के लिए विशिष्ट हो
- हर खंड में फसल का नाम स्पष्ट रूप से शामिल करें
- इस विशिष्ट फसल के लिए वास्तविक NPK अनुपात, बुवाई की गहराई और दूरी का संदर्भ दें
- वास्तविक परिपक्वता दिन और कटाई का समय बताएं
- क्षेत्र के अनुसार सिंचाई और कीट प्रबंधन सलाह दें
- सामग्री व्यावहारिक और किसान के अनुकूल रखें
- भाषाएं मिश्रित न करें। केवल हिंदी का उपयोग करें।

केवल JSON के साथ जवाब दें (कोई मार्कडाउन नहीं, कोई कोड ब्लॉक नहीं):
{
  "seasonal_plan": "इस फसल के लिए विशिष्ट खेत की तैयारी, बुवाई की गहराई और दूरी",
  "fertilizer_schedule": "इस फसल के लिए NPK अनुपात और अनुप्रयोग अनुसूची",
  "pest_watch": "इस विशिष्ट फसल के लिए सामान्य कीट और रोग",
  "harvest_window": "बुवाई की तारीख के आधार पर अपेक्षित परिपक्वता और कटाई का समय",
  "tips": "इस फसल के लिए विशिष्ट सिंचाई आवश्यकताएं और प्रबंधन सुझाव"
}""",

    "te": """తెలుగులో మాత్రమే సమాధానం ఇవ్వండి. ఆంగ్లం లేదు.

మీరు భారతీయ రైతులకు పంట-నిర్దిష్ట మార్గదర్శనం అందించే వ్యవసాయ నిపుణుడు.

ముఖ్యమైన సూచనలు:
- అన్ని సమాధానాలు తెలుగులో మాత్రమే ఉండాలి
- ఈ 5 కీలు ఉన్న చెల్లుబాటుయ్యే JSON మాత్రమే ఉత్పత్తి చేయండి: seasonal_plan, fertilizer_schedule, pest_watch, harvest_window, tips
- అందించిన పంట, ప్రదేశం మరియు విత్తన తేదీకి ప్రతిక్రియ నిర్దిష్టమైనది
- ప్రతి విభాగంలో పంట పేరు స్పష్టంగా చేర్చండి
- ఈ నిర్దిష్ట పంటకు వాస్తవ NPK నిష్పత్తి, విత్తన లోతు మరియు దూరాన్ని సూచించండి
- వాస్తవిక పరిపక్వత రోజులు మరియు కోత సమయం తెలియజేయండి
- ప్రాంత-అనుకూల సేద మరియు తెగుళ్ల నిర్వహణ సలహా ఇవ్వండి
- విషయవస్తువు ఆచరణాత్మకమైనది మరియు రైతు-స్నేహపూర్వకమైనది
- భాషలను కలపవద్దు. తెలుగు మాత్రమే ఉపయోగించండి.

JSON తో మాత్రమే సమాధానం ఇవ్వండి (మార్కడౌన్ లేదు, కోడ్ బ్లాక్‌లు లేవు):
{
  "seasonal_plan": "ఈ పంటకు నిర్దిష్ట క్షేత్ర సిద్ధీకరణ, విత్తన లోతు మరియు దూరం",
  "fertilizer_schedule": "ఈ పంటకు NPK నిష్పత్తి మరియు అనువర్తన షెడ్యూల్",
  "pest_watch": "ఈ నిర్దిష్ట పంటకు సాధారణ తెగుళ్లు మరియు వ్యాధులు",
  "harvest_window": "విత్తన తేదీ ఆధారంగా ఆశించిన పరిపక్వత మరియు కోత సమయం",
  "tips": "ఈ పంటకు నిర్దిష్ట సేద అవసరాలు మరియు నిర్వహణ సుझావులు"
}""",
}

# Comprehensive crop knowledge base
CROP_KNOWLEDGE_BASE = {
    "Wheat/गेहूं": {
        "en": {
            "maturity_days": "120-150",
            "common_pests": "Armyworm, Aphids, Shoot fly, Termites",
            "common_diseases": "Rust, Powdery mildew, Septoria leaf blotch",
            "npk_ratio": "120:60:40",
            "fertilizer_timing": "Basal at sowing, 1st split at 4-6 weeks, 2nd split at 8-10 weeks",
            "irrigation": "3-4 irrigations at CRI, tillering, boot stage, grain filling",
            "seed_rate": "100-125 kg/ha",
            "planting_depth": "3-4 cm",
            "spacing": "20-23 cm between rows"
        },
        "hi": {
            "maturity_days": "120-150 दिन",
            "common_pests": "आर्मीवर्म, एफिड्स, शूट फ्लाई, दीमक",
            "common_diseases": "जंग, पाउडरी मिल्ड्यू, सेप्टोरिया पत्ती धब्बा",
            "npk_ratio": "120:60:40",
            "fertilizer_timing": "बुवाई पर, 4-6 सप्ताह पर, 8-10 सप्ताह पर",
            "irrigation": "CRI, कल्लों निकलते समय, बूट स्टेज, दानों भरते समय 3-4 सिंचाई",
            "seed_rate": "100-125 किग्रा/हेक्टेयर",
            "planting_depth": "3-4 सेमी",
            "spacing": "पंक्तियों के बीच 20-23 सेमी"
        }
    },
    "Rice/धान": {
        "en": {
            "maturity_days": "100-150",
            "common_pests": "Leaf folder, Plant hopper, Stem borer",
            "common_diseases": "Blast, Sheath rot, Bacterial leaf streak",
            "npk_ratio": "80:40:40",
            "fertilizer_timing": "Basal, at panicle initiation, at heading",
            "irrigation": "Continuous submergence, drain 10-15 days before harvest",
            "seed_rate": "60-80 kg/ha (transplanted), 120-150 kg/ha (direct)",
            "planting_depth": "2-3 cm",
            "spacing": "20-25 cm x 15-20 cm for transplanted rice"
        }
    },
    "Maize/मक्का": {
        "en": {
            "maturity_days": "90-120",
            "common_pests": "Stem borer, Fall armyworm, Shoot fly",
            "common_diseases": "Leaf blight, Rust, Stalk rot",
            "npk_ratio": "120:60:60",
            "fertilizer_timing": "At sowing, 4-6 weeks, at tasseling",
            "irrigation": "6-8 irrigations, critical at tasseling and silking",
            "seed_rate": "20-25 kg/ha",
            "planting_depth": "5-7 cm",
            "spacing": "60-75 cm x 20-25 cm"
        }
    },
    "Cotton/कपास": {
        "en": {
            "maturity_days": "160-200",
            "common_pests": "Bollworm, Jassids, Whiteflies",
            "common_diseases": "Leaf curl, Wilt, Anthracnose",
            "npk_ratio": "100:50:50",
            "fertilizer_timing": "Basal, at flowering, at boll formation",
            "irrigation": "6-8 irrigations, critical at flowering",
            "seed_rate": "20-25 kg/ha",
            "planting_depth": "2-3 cm",
            "spacing": "90-120 cm x 45-60 cm"
        }
    },
    "Sugarcane/गन्ना": {
        "en": {
            "maturity_days": "300-360",
            "common_pests": "Stem borer, Scale insect, Shoot fly",
            "common_diseases": "Red rot, Smut, Wilt",
            "npk_ratio": "150:60:40",
            "fertilizer_timing": "Basal, at 4-6 months, at 8-10 months",
            "irrigation": "12-16 irrigations, critical at sprouting",
            "seed_rate": "45-60 tonnes/ha",
            "planting_depth": "3-5 cm",
            "spacing": "90-120 cm between rows"
        }
    },
    "Groundnut/मूंगफली": {
        "en": {
            "maturity_days": "120-150",
            "common_pests": "Leaf miner, Aphids, Jassids",
            "common_diseases": "Leaf spot, Rust, Stem rot",
            "npk_ratio": "20:50:40",
            "fertilizer_timing": "Basal at sowing, no split doses",
            "irrigation": "3-4 irrigations, critical at flowering",
            "seed_rate": "40-50 kg/ha",
            "planting_depth": "4-5 cm",
            "spacing": "30-45 cm x 10-15 cm"
        }
    },
    "Tomato/टमाटर": {
        "en": {
            "maturity_days": "70-90",
            "common_pests": "Fruit borer, Whiteflies, Jassids",
            "common_diseases": "Early blight, Late blight, Wilt",
            "npk_ratio": "100:50:100",
            "fertilizer_timing": "At planting, 30 days, 60 days",
            "irrigation": "Drip irrigation, frequent and light",
            "seed_rate": "500-700 gram/ha",
            "planting_depth": "Seedlings, 45-60 cm",
            "spacing": "60-90 cm x 45-60 cm"
        }
    },
    "Onion/प्याज": {
        "en": {
            "maturity_days": "120-150",
            "common_pests": "Thrips, Stem fly, Spider mite",
            "common_diseases": "Purple blotch, Pink root, Fusarium rot",
            "npk_ratio": "80:80:80",
            "fertilizer_timing": "Basal, 30 days, 60 days after planting",
            "irrigation": "8-10 irrigations, frequent and light",
            "seed_rate": "6-8 kg/ha",
            "planting_depth": "Just below soil surface",
            "spacing": "15-20 cm between rows"
        }
    },
}

def _validate_sowing_date(crop: str, sowing_date: str, lang: str = "en") -> Tuple[bool, str]:
    """
    Validate if the sowing date is agronomically appropriate for the crop.
    
    Returns:
        Tuple of (is_valid, warning_message in specified language)
    """
    try:
        sowing_datetime = datetime.strptime(sowing_date, "%Y-%m-%d")
        month = sowing_datetime.month
        
        # Extract base crop name (before slash)
        crop_base = crop.split("/")[0].strip()
        
        for crop_name, season_info in CROP_SEASONS.items():
            if crop_base.lower() in crop_name.lower():
                start = season_info["start_month"]
                end = season_info["end_month"]
                
                # Check if month is within recommended range
                if start <= end:
                    if not (start <= month <= end):
                        warnings_dict = season_info.get("warnings", {})
                        return False, warnings_dict.get(lang, warnings_dict.get("en", "Sowing date is off-season."))
                else:
                    if not (month >= start or month <= end):
                        warnings_dict = season_info.get("warnings", {})
                        return False, warnings_dict.get(lang, warnings_dict.get("en", "Sowing date is off-season."))
                
                return True, ""
        
        return True, ""
    except Exception:
        return True, ""

def _extract_json_from_response(response: str) -> Optional[dict]:
    """Extract and parse JSON from LLM response with auto-repair."""
    try:
        return json.loads(response)
    except:
        pass
    
    # Try to find JSON in response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json.loads(json_str)
        except:
            return None
    
    return None

def _generate_response_from_knowledge_base(
    crop: str, district: str, state: str, sowing_date: str, lang: str
) -> dict:
    """Generate response using knowledge base when LLM fails."""
    crop_info = CROP_KNOWLEDGE_BASE.get(crop, {}).get("en", {})
    
    if lang == "hi":
        seasonal = f"खेत की तैयारी:\n{crop} के लिए मिट्टी को अच्छी तरह तैयार करें। बुवाई की गहराई: {crop_info.get('planting_depth', '3-4 सेमी')}। पंक्ति की दूरी: {crop_info.get('spacing', '20-23 सेमी')}। {district}, {state} में बुवाई {sowing_date} को करें।"
        fertilizer = f"उर्वरक योजना:\nNPK अनुपात {crop_info.get('npk_ratio', '120:60:40')} का उपयोग करें।\nआवेदन समय: {crop_info.get('fertilizer_timing', 'बुवाई पर, 4-6 सप्ताह, 8-10 सप्ताह')}"
        pests = f"कीट और रोग नियंत्रण:\nकीट: {crop_info.get('common_pests', 'विभिन्न कीट')}\nरोग: {crop_info.get('common_diseases', 'विभिन्न रोग')}\nनियमित निरीक्षण अवश्यक है।"
        harvest = f"कटाई का समय:\nपरिपक्वता अवधि: {crop_info.get('maturity_days', '120-150 दिन')}\n{sowing_date} से लगभग {crop_info.get('maturity_days', 'X')} दिन बाद कटाई के लिए तैयार।"
        tips = f"महत्वपूर्ण सुझाव:\nसिंचाई: {crop_info.get('irrigation', 'आवश्यकतानुसार')}\nसमय पर निराई-गुड़ाई करें।"
    elif lang == "te":
        seasonal = f"క్షేత్ర సిద్ధీకరణ:\n{crop} కోసం నేల చక్కగా సిద్ధం చేయండి. విత్తన లోతు: {crop_info.get('planting_depth', '3-4 సెం.మీ.')}. అడ్డం దూరం: {crop_info.get('spacing', '20-23 సెం.మీ.')}. {district}, {state}లో {sowing_date}న విత్తనం చేయండి."
        fertilizer = f"ఎరువు షెడ్యూల్:\nNPK నిష్పత్తి {crop_info.get('npk_ratio', '120:60:40')} ఉపయోగించండి.\nప్రయోగ సమయం: {crop_info.get('fertilizer_timing', 'విత్తన సమయం, 4-6 వారాలు, 8-10 వారాలు')}"
        pests = f"తెగుళ్ల నిర్వహణ:\nతెగులు: {crop_info.get('common_pests', 'వివిధ తెగులు')}\nరోగాలు: {crop_info.get('common_diseases', 'వివిధ రోగాలు')}\nনिয়মिত పర్యవేక్షణ సిఫారసు చేయబడుతుంది."
        harvest = f"కోత విండो:\nపరిపక్వత: {crop_info.get('maturity_days', '120-150 రోజులు')}\n{sowing_date} నుండి సుమారు {crop_info.get('maturity_days', 'X')} రోజుల తర్వాత {crop} కోసం సిద్ధంగా ఉంటుంది."
        tips = f"చిట్కాలు:\nసేద: {crop_info.get('irrigation', 'అవసరమైనంతవరకు')}\nసమయానికి కలుపు కోయండి."
    else:  # Default to English
        seasonal = f"Field preparation:\nPrepare soil thoroughly for {crop}. Planting depth: {crop_info.get('planting_depth', '3-4 cm')}. Row spacing: {crop_info.get('spacing', '20-23 cm')}. Sow on {sowing_date} in {district}, {state}."
        fertilizer = f"Fertilizer schedule:\nApply NPK {crop_info.get('npk_ratio', '120:60:40')}.\nTiming: {crop_info.get('fertilizer_timing', 'At sowing, 4-6 weeks, 8-10 weeks')}"
        pests = f"Pest management:\nPests: {crop_info.get('common_pests', 'various pests')}\nDiseases: {crop_info.get('common_diseases', 'various diseases')}\nMonitoring recommended."
        harvest = f"Harvest window:\nMaturity: {crop_info.get('maturity_days', '120-150 days')}\n{crop} ready approximately {crop_info.get('maturity_days', 'X')} days after {sowing_date}."
        tips = f"Tips:\nIrrigation: {crop_info.get('irrigation', 'as needed')}\nPerform timely weeding."
    
    return {
        "seasonal_plan": seasonal,
        "fertilizer_schedule": fertilizer,
        "pest_watch": pests,
        "harvest_window": harvest,
        "tips": tips
    }

def get_crop_advice(
    crop: str,
    district: str,
    state: str,
    sowing_date: str,
    lang: str = "en",
    settings: dict = None
) -> dict:
    """
    Get comprehensive crop advice with date validation and Claude fallback.
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3.2:1b"}
    
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    
    # Validate sowing date (with language-specific warning)
    is_valid, date_warning = _validate_sowing_date(crop, sowing_date, lang)
    
    result = {}
    if not is_valid:
        result["date_warning"] = date_warning
    
    try:
        system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        crop_info = CROP_KNOWLEDGE_BASE.get(crop, {}).get("en", {})
        
        crop_data = f"""CROP: {crop} | NPK: {crop_info.get('npk_ratio')} | Maturity: {crop_info.get('maturity_days')} | Pests: {crop_info.get('common_pests')}"""
        
        prompt = f"""Crop: {crop} | Location: {district}, {state} | Sowing: {sowing_date}

{crop_data}

Provide detailed crop-specific advice."""
        
        # Try Ollama first
        response = get_response(prompt, system_prompt, settings)
        
        if response and not response.startswith("Error"):
            parsed = _extract_json_from_response(response)
            if parsed and all(k in parsed for k in ["seasonal_plan", "fertilizer_schedule", "pest_watch", "harvest_window", "tips"]):
                result.update(parsed)
                return result
        
        # Ollama failed - try Claude API fallback
        print("⚡ Using Claude API fallback...")
        claude_response = get_claude_response(prompt, system_prompt)
        
        if claude_response and not claude_response.startswith("Error"):
            parsed = _extract_json_from_response(claude_response)
            if parsed and all(k in parsed for k in ["seasonal_plan", "fertilizer_schedule", "pest_watch", "harvest_window", "tips"]):
                result.update(parsed)
                return result
        
        # Both LLMs failed - use knowledge base
        kb_response = _generate_response_from_knowledge_base(crop, district, state, sowing_date, lang)
        result.update(kb_response)
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        kb_response = _generate_response_from_knowledge_base(crop, district, state, sowing_date, lang)
        result.update(kb_response)
        return result
