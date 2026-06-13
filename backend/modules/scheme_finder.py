"""
Scheme Finder module - Helps farmers discover relevant government schemes and subsidies.
"""

import sys
import os
from typing import Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_response
from config import SUPPORTED_LANGUAGES, INDIAN_STATES, GOVERNMENT_SCHEMES

# Comprehensive government schemes database
SCHEMES_DATABASE = {
    "central": [
        {
            "name": "PM-KISAN",
            "full_name": "Pradhan Mantri Kisan Samman Nidhi",
            "description": "Income support scheme for farmer families",
            "benefit": "₹6,000 per year in 3 equal installments of ₹2,000 each",
            "eligibility": "All landholding farmer families with cultivable land",
            "exclusion": "Institutional landholders, former and present constitutional post holders, professionals like doctors, engineers, lawyers",
            "how_to_apply": "Register through Common Service Centres (CSCs) or visit local agriculture department office with land records",
            "documents_required": ["Aadhaar card", "Land records", "Bank account details", "Mobile number"]
        },
        {
            "name": "PMFBY",
            "full_name": "Pradhan Mantri Fasal Bima Yojana",
            "description": "Comprehensive crop insurance scheme",
            "benefit": "Insurance coverage for crop loss due to natural calamities, pests, and diseases",
            "eligibility": "All farmers growing notified crops including sharecroppers and tenant farmers",
            "exclusion": "None - all farmers are eligible",
            "how_to_apply": "Approach bank, insurance company, or Common Service Centre during enrollment period",
            "documents_required": ["Aadhaar card", "Land records or tenant agreement", "Bank account details", "Crop sowing proof"]
        },
        {
            "name": "KCC",
            "full_name": "Kisan Credit Card",
            "description": "Credit facility for farmers",
            "benefit": "Credit up to ₹3 lakhs at 4% interest rate, crop loans, working capital",
            "eligibility": "All farmers including individual farmers, joint borrowers, tenant farmers, sharecroppers",
            "exclusion": "None - all farmers are eligible",
            "how_to_apply": "Apply at any bank branch with required documents",
            "documents_required": ["Aadhaar card", "Land records", "Passport size photographs", "Identity proof", "Address proof"]
        },
        {
            "name": "PM-KUSUM",
            "full_name": "Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan",
            "description": "Solar power scheme for farmers",
            "benefit": "Subsidy for solar pumps and grid connection, additional income from solar power generation",
            "eligibility": "Individual farmers with grid-connected agricultural pumps",
            "exclusion": "Farmers without agricultural electricity connections",
            "how_to_apply": "Apply through state nodal agency or DISCOM",
            "documents_required": ["Aadhaar card", "Land records", "Electricity bill", "Bank account details"]
        },
        {
            "name": "NMSA",
            "full_name": "National Mission for Sustainable Agriculture",
            "description": "Promotes sustainable agriculture practices",
            "benefit": "Financial assistance for organic farming, soil health, water conservation",
            "eligibility": "Farmers adopting sustainable practices",
            "exclusion": "Varies by component",
            "how_to_apply": "Contact State Agriculture Department or visit KVK",
            "documents_required": ["Aadhaar card", "Land records", "Project proposal"]
        }
    ],
    "state_specific": {
        "Punjab": [
            {
                "name": "PAU Scheme",
                "full_name": "Punjab Agricultural University Extension",
                "description": "Technical support and subsidies for Punjab farmers",
                "benefit": "Subsidized seeds, equipment, and technical guidance",
                "eligibility": "Punjab farmers",
                "how_to_apply": "Contact PAU or local agriculture department"
            }
        ],
        "Haryana": [
            {
                "name": "HACOS",
                "full_name": "Haryana Cooperative Societies",
                "description": "Cooperative support for farmers",
                "benefit": "Low-interest loans, input subsidies",
                "eligibility": "Haryana farmers who are cooperative members",
                "how_to_apply": "Join local cooperative society"
            }
        ],
        "Maharashtra": [
            {
                "name": "Maha-DBT",
                "full_name": "Maharashtra Direct Benefit Transfer",
                "description": "Direct benefit transfer for various agricultural schemes",
                "benefit": "Direct cash transfers for inputs, equipment",
                "eligibility": "Maharashtra farmers with registered land",
                "how_to_apply": "Register on Maha-DBT portal"
            }
        ],
        "Karnataka": [
            {
                "name": "Raitha Samrudhi",
                "full_name": "Karnataka Raitha Samrudhi Yojana",
                "description": "Income support for Karnataka farmers",
                "benefit": "₹25,000 per year for eligible farmers",
                "eligibility": "Karnataka farmers with land",
                "how_to_apply": "Register through Raitha Samrudhi portal"
            }
        ],
        "Telangana": [
            {
                "name": "Rythu Bandhu",
                "full_name": "Telangana Rythu Bandhu",
                "description": "Investment support for farmers",
                "benefit": "₹10,000 per acre per year (₹5,000 per season)",
                "eligibility": "Telangana farmers with cultivable land",
                "how_to_apply": "Register through Rythu Bandhu portal with land records"
            }
        ],
        "Andhra Pradesh": [
            {
                "name": "YSR Rythu Bharosa",
                "full_name": "YSR Rythu Bharosa-PM KISAN",
                "description": "Income support for AP farmers",
                "benefit": "₹13,500 per year (₹7,500 from state + ₹6,000 from PM-KISAN)",
                "eligibility": "AP farmers with land",
                "how_to_apply": "Register through YSR Rythu Bharosa portal"
            }
        ],
        "Tamil Nadu": [
            {
                "name": "TN-KISAN",
                "full_name": "Tamil Nadu Kisan Scheme",
                "description": "State-level income support",
                "benefit": "Additional income support along with PM-KISAN",
                "eligibility": "Tamil Nadu farmers",
                "how_to_apply": "Register through Tamil Nadu agriculture portal"
            }
        ],
        "Kerala": [
            {
                "name": "Kerala Karshaka",
                "full_name": "Kerala Karshaka Pension Scheme",
                "description": "Pension and support for Kerala farmers",
                "benefit": "Monthly pension and various subsidies",
                "eligibility": "Kerala farmers above 60 years",
                "how_to_apply": "Apply through Kerala agriculture department"
            }
        ],
        "Uttar Pradesh": [
            {
                "name": "UP-KISAN",
                "full_name": "Uttar Pradesh Kisan Kalyan Yojana",
                "description": "State support for UP farmers",
                "benefit": "Additional benefits over PM-KISAN",
                "eligibility": "UP farmers with land records",
                "how_to_apply": "Register through UP agriculture portal"
            }
        ]
    }
}

# Language-specific system prompts
SYSTEM_PROMPTS = {
    "en": """You are an expert in Indian government agricultural schemes and subsidies. 
    Help farmers identify the most relevant schemes based on their specific situation.
    Provide clear, accurate information about eligibility, benefits, and application processes.
    Always respond in English.""",
    
    "hi": """आप भारतीय सरकारी कृषि योजनाओं और सब्सिडी के विशेषज्ञ हैं।
    किसानों को उनकी विशिष्ट स्थिति के आधार पर सबसे प्रासंगिक योजनाओं की पहचान करने में मदद करें।
    पात्रता, लाभ और आवेदन प्रक्रिया के बारे में स्पष्ट, सटीक जानकारी प्रदान करें।
    हमेशा हिंदी में उत्तर दें।""",
    
    "te": """మీరు భారత ప్రభుత్వ వ్యవసాయ పథకాలు మరియు సబ్సిడీల నిపుణులు.
    రైతులకు వారి నిర్దిష్ట పరిస్థితి ఆధారంగా అత్యంత సంబంధిత పథకాలను గుర్తించడంలో సహాయం చేయండి.
    అర్హత, ప్రయోజనాలు మరియు దరఖాస్తు ప్రక్రియల గురించి స్పష్టమైన, ఖచ్చితమైన సమాచారాన్ని అందించండి.
    ఎల్లప్పుడూ తెలుగులో స్పందించండి.""",
}

def find_schemes(
    state: str,
    crop: str,
    land_size: float,
    lang: str = "en",
    settings: dict = None
) -> List[Dict]:
    """
    Find relevant government schemes for a farmer based on their profile.
    
    Args:
        state: Farmer's state
        crop: Crop they are growing
        land_size: Land size in acres
        lang: Language code ("en", "hi", or "te")
        settings: AI provider settings dictionary
    
    Returns:
        List[Dict]: List of relevant schemes with scheme_name, eligibility, benefit, how_to_apply
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}
    
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    
    try:
        # First, get relevant schemes from the database
        relevant_schemes = _get_relevant_schemes_from_db(state, crop, land_size)
        
        # Use AI to provide personalized recommendations and explanations
        ai_recommendations = _get_ai_recommendations(state, crop, land_size, lang, settings)
        
        # Combine database info with AI recommendations
        result = []
        for scheme in relevant_schemes:
            scheme_info = {
                "scheme_name": scheme.get("name", scheme.get("scheme_name", "")),
                "eligibility": scheme.get("eligibility", ""),
                "benefit": scheme.get("benefit", ""),
                "how_to_apply": scheme.get("how_to_apply", "")
            }
            
            # Add AI-generated personalized advice if available
            if ai_recommendations and scheme_info["scheme_name"] in ai_recommendations:
                scheme_info["ai_advice"] = ai_recommendations[scheme_info["scheme_name"]]
            
            result.append(scheme_info)
        
        return result
        
    except Exception as e:
        # Return basic schemes on error
        return _get_basic_schemes(lang)


def _get_relevant_schemes_from_db(state: str, crop: str, land_size: float) -> List[Dict]:
    """
    Get relevant schemes from the database based on farmer profile.
    """
    relevant_schemes = []
    
    # Always include central schemes
    relevant_schemes.extend(SCHEMES_DATABASE["central"])
    
    # Add state-specific schemes
    state_schemes = SCHEMES_DATABASE["state_specific"].get(state, [])
    relevant_schemes.extend(state_schemes)
    
    # Add nearby state schemes (simplified - in reality would need proper mapping)
    # For now, just return the schemes we found
    
    return relevant_schemes


def _get_ai_recommendations(state: str, crop: str, land_size: float, lang: str, settings: dict) -> Dict:
    """
    Get AI-generated personalized recommendations for schemes.
    """
    try:
        if lang == "hi":
            prompt = f"""किसान प्रोफ़ाइल:
- राज्य: {state}
- फसल: {crop}
- भूमि आकार: {land_size} एकड़

इस किसान के लिए सबसे उपयुक्त सरकारी योजनाओं की सिफारिश करें और बताएं कि वे प्रत्येक योजना से कैसे लाभान्वित हो सकते हैं।
प्रत्येक योजना के लिए:
1. योजना का नाम
2. क्यों उपयुक्त है
3. आवेदन के लिए महत्वपूर्ण टिप्स

सिर्फ 3-4 सबसे महत्वपूर्ण योजनाओं पर ध्यान केंद्रित करें।"""
        
        elif lang == "te":
            prompt = f"""రైతు ప్రొఫైల్:
- రాష్ట్రం: {state}
- పంట: {crop}
- భూమి పరిమాణం: {land_size} ఎకరాలు

ఈ రైతుకు అత్యంత అనుకూలమైన ప్రభుత్వ పథకాలను సిఫార్సు చేయండి మరియు వారు ప్రతి పథకం నుండి ఎలా ప్రయోజనం పొందవచ్చో వివరించండి.
ప్రతి పథకానికి:
1. పథకం పేరు
2. ఎందుకు అనుకూలం
3. దరఖాస్తు చేసుకోవడానికి ముఖ్యమైన చిట్కాలు

కేవలం 3-4 అత్యంత ముఖ్యమైన పథకాలపై దృష్టి పెట్టండి.""",
        
        else:
            prompt = f"""Farmer Profile:
- State: {state}
- Crop: {crop}
- Land Size: {land_size} acres

Recommend the most suitable government schemes for this farmer and explain how they can benefit from each.
For each scheme, provide:
1. Scheme name
2. Why it's suitable
3. Important application tips

Focus on only 3-4 most important schemes.""",
        
        system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        
        response = get_response(prompt, system_prompt, settings)
        
        # Parse AI response to extract scheme recommendations
        # This is a simplified parsing - in production would need more sophisticated NLP
        recommendations = {}
        lines = response.split('\n')
        current_scheme = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ["pm-kisan", "pmfby", "kcc", "rythu", "kusum"]):
                current_scheme = line.split(":")[0].strip()
                recommendations[current_scheme] = line
            elif current_scheme and line:
                recommendations[current_scheme] = recommendations.get(current_scheme, "") + " " + line
        
        return recommendations
        
    except Exception:
        return {}


def _get_basic_schemes(lang: str) -> List[Dict]:
    """
    Return basic scheme information when detailed lookup fails.
    """
    basic_schemes = []
    
    for scheme in SCHEMES_DATABASE["central"][:3]:  # Top 3 central schemes
        if lang == "hi":
            basic_schemes.append({
                "scheme_name": scheme["name"],
                "eligibility": "सभी किसान पात्र हैं",
                "benefit": scheme["benefit"],
                "how_to_apply": "स्थानीय कृषि विभाग से संपर्क करें"
            })
        elif lang == "te":
            basic_schemes.append({
                "scheme_name": scheme["name"],
                "eligibility": "అన్ని రైతులు అర్హులు",
                "benefit": scheme["benefit"],
                "how_to_apply": "స్థానిక వ్యవసాయ శాఖను సంప్రదించండి"
            })
        else:
            basic_schemes.append({
                "scheme_name": scheme["name"],
                "eligibility": "All farmers are eligible",
                "benefit": scheme["benefit"],
                "how_to_apply": "Contact local agriculture department"
            })
    
    return basic_schemes


def get_scheme_application_guidance(scheme_name: str, lang: str = "en", settings: dict = None) -> str:
    """
    Get detailed application guidance for a specific scheme.
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}
    
    try:
        # Find scheme in database
        scheme_info = None
        for scheme in SCHEMES_DATABASE["central"]:
            if scheme["name"].lower() == scheme_name.lower():
                scheme_info = scheme
                break
        
        if not scheme_info:
            # Check state-specific schemes
            for state_schemes in SCHEMES_DATABASE["state_specific"].values():
                for scheme in state_schemes:
                    if scheme["name"].lower() == scheme_name.lower():
                        scheme_info = scheme
                        break
        
        if not scheme_info:
            return f"Scheme '{scheme_name}' not found in database."
        
        if lang == "hi":
            guidance = f"""{scheme_info['full_name']} ({scheme_info['name']})

लाभ: {scheme_info['benefit']}

पात्रता: {scheme_info['eligibility']}

आवेदन प्रक्रिया:
{scheme_info['how_to_apply']}

आवश्यक दस्तावेज:
{', '.join(scheme_info.get('documents_required', ['आधार कार्ड', 'भूमि रिकॉर्ड', 'बैंक विवरण']))}

महत्वपूर्ण टिप्स:
- आवेदन से पहले सभी दस्तावेज तैयार रखें
- आधिकारिक वेबसाइट या स्थानीय कृषि विभाग से नवीनतम जानकारी जांचें
- आवेदन की स्थिति ऑनलाइन ट्रैक करें"""
        
        elif lang == "te":
            guidance = f"""{scheme_info['full_name']} ({scheme_info['name']})

ప్రయోజనం: {scheme_info['benefit']}

అర్హత: {scheme_info['eligibility']}

దరఖాస్తు ప్రక్రియ:
{scheme_info['how_to_apply']}

అవసరమైన పత్రాలు:
{', '.join(scheme_info.get('documents_required', ['ఆధార్ కార్డ్', 'భూమి రికార్డులు', 'బ్యాంకు వివరాలు']))}

ముఖ్యమైన చిట్కాలు:
- దరఖాస్తు చేసుకునే ముందు అన్ని పత్రాలను సిద్ధం చేసుకోండి
- అధికారిక వెబ్‌సైట్ లేదా స్థానిక వ్యవసాయ శాఖ నుండి తాజా సమాచారాన్ని తనిఖీ చేయండి
- దరఖాస్తు స్థితిని ఆన్‌లైన్‌లో ట్రాక్ చేయండి"""
        
        else:
            guidance = f"""{scheme_info['full_name']} ({scheme_info['name']})

Benefit: {scheme_info['benefit']}

Eligibility: {scheme_info['eligibility']}

Application Process:
{scheme_info['how_to_apply']}

Required Documents:
{', '.join(scheme_info.get('documents_required', ['Aadhaar card', 'Land records', 'Bank details']))}

Important Tips:
- Prepare all documents before applying
- Check latest information from official website or local agriculture department
- Track application status online"""
        
        return guidance
        
    except Exception as e:
        return f"Error getting guidance: {str(e)}"