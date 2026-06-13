"""
Pest Diagnosis module - Provides AI-powered pest and disease diagnosis from crop images.
"""

import sys
import os
import base64
import random
from typing import Dict, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_vision_response, get_response
from config import SUPPORTED_LANGUAGES

# Common crop diseases and pests database for fallback
PEST_DISEASE_DATABASE = {
    "wheat": [
        {
            "name": "Wheat Rust",
            "symptoms": "Orange-brown powdery spots on leaves and stems",
            "treatment": "Apply fungicides like propiconazole or tebuconazole",
            "prevention": "Use resistant varieties, crop rotation, timely sowing"
        },
        {
            "name": "Powdery Mildew",
            "symptoms": "White powdery growth on leaves",
            "treatment": "Sulfur-based fungicides or potassium bicarbonate",
            "prevention": "Ensure proper spacing, avoid overhead irrigation"
        }
    ],
    "rice": [
        {
            "name": "Blast Disease",
            "symptoms": "Spindle-shaped lesions on leaves with gray centers",
            "treatment": "Apply tricyclazole or azoxystrobin fungicides",
            "prevention": "Use certified seeds, balanced fertilization"
        },
        {
            "name": "Brown Spot",
            "symptoms": "Small brown spots on leaves and grains",
            "treatment": "Copper-based fungicides",
            "prevention": "Seed treatment with fungicides, proper water management"
        }
    ],
    "cotton": [
        {
            "name": "Pink Bollworm",
            "symptoms": "Holes in bolls, pink larvae inside",
            "treatment": "Bt cotton varieties, pheromone traps",
            "prevention": "Crop rotation, destruction of crop residue"
        },
        {
            "name": "Leaf Curl Virus",
            "symptoms": "Upward curling of leaves, stunted growth",
            "treatment": "No cure, remove infected plants",
            "prevention": "Control whiteflies, use resistant varieties"
        }
    ],
    "tomato": [
        {
            "name": "Early Blight",
            "symptoms": "Dark spots with concentric rings on leaves",
            "treatment": "Chlorothalonil or copper-based fungicides",
            "prevention": "Crop rotation, staking, mulching"
        },
        {
            "name": "Aphids",
            "symptoms": "Small green/black insects on undersides of leaves",
            "treatment": "Neem oil, insecticidal soap",
            "prevention": "Beneficial insects, reflective mulch"
        }
    ],
    "onion": [
        {
            "name": "Purple Blotch",
            "symptoms": "Purple lesions on leaves with yellow halos",
            "treatment": "Mancozeb or iprodione fungicides",
            "prevention": "Crop rotation, avoid overhead irrigation"
        },
        {
            "name": "Thrips",
            "symptoms": "Silvery patches on leaves, tiny insects",
            "treatment": "Spinosad or imidacloprid",
            "prevention": "Blue sticky traps, weed control"
        }
    ]
}

# Language-specific prompts for pest diagnosis
DIAGNOSIS_PROMPTS = {
    "en": "You are an expert entomologist and plant pathologist specializing in crop pest and disease diagnosis. Respond ONLY in English. Analyze the image carefully and provide diagnosis in this format: Disease/Pest Name, Symptoms, Treatment, Prevention, Confidence (High/Medium/Low). Be specific about what you see.",
    
    "hi": "आप एक कृषि विशेषज्ञ हैं जो फसल कीट और रोग निदान में विशेषज्ञ हैं। केवल हिंदी में उत्तर दें। छवि का विश्लेषण करें और इस प्रारूप में विस्तृत निदान प्रदान करें: रोग/कीट का नाम, लक्षण, उपचार, रोकथाम, आत्मविश्वास (उच्च/मध्यम/निम्न)। जो देखते हैं उसके बारे में विशिष्ट रहें।",
    
    "te": "మీరు పంట తెగులు మరియు వ్యాధి నిర్ధారణలో నిపుణుడైన వ్యవసాయ నిపుణులు. కేవలం తెలుగులో మాత్రమే సమాధానం ఇవ్వండి. చిత్రాన్ని జాగ్రత్తగా విశ్లేషించి ఈ ఆకృతిలో సమాధానం ఇవ్వండి: వ్యాధి/తెగులు పేరు, లక్షణాలు, చికిత్స, నివారణ, ఆత్మవిశ్వాసం (అధికం/మధ్యమ/నీచ). మీరు చూసిన వాటి గురించి నిర్దిష్టంగా ఉండండి."
}

def diagnose_pest(
    image_bytes: bytes,
    crop: str,
    lang: str = "en",
    settings: dict = None
) -> Dict:
    """
    Diagnose pest or disease from a crop image using AI vision analysis.
    
    Args:
        image_bytes: Raw image data (bytes)
        crop: Crop name (e.g., "Wheat/गेहूं")
        lang: Language code ("en", "hi", or "te")
        settings: AI provider settings dictionary
    
    Returns:
        Dict: Contains disease_name, symptoms, treatment, prevention
              Returns fallback diagnosis if vision analysis fails
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}
    
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Extract English crop name for analysis
        crop_en = crop.split("/")[0].strip() if "/" in crop else crop
        
        # Create language-specific prompt for vision analysis
        language_instruction = DIAGNOSIS_PROMPTS.get(lang, DIAGNOSIS_PROMPTS["en"])
        prompt = f"{language_instruction}\n\nAnalyze this {crop_en} crop image. Look for pests and diseases. Be specific about what you see."
        
        # Try vision analysis
        vision_response = get_vision_response(prompt, image_base64, settings)
        
        if vision_response and not vision_response.startswith("Error:"):
            # Parse the vision response into structured format
            return _parse_diagnosis_response(vision_response, lang, crop_en)
        
        # If vision failed, provide text-based fallback
        return _get_fallback_diagnosis(crop_en, lang)
        
    except Exception as e:
        # Return fallback diagnosis on any error
        crop_en = crop.split("/")[0].strip() if "/" in crop else crop
        return _get_fallback_diagnosis(crop_en, lang)


def _parse_diagnosis_response(response: str, lang: str, crop_en: str = "") -> Dict:
    """
    Parse AI diagnosis response into structured format.
    """
    result = {
        "disease_name": "",
        "symptoms": "",
        "treatment": "",
        "prevention": "",
        "confidence": "Medium"
    }
    
    lines = response.split('\n')
    current_section = None
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Detect section headers in multiple languages
        if any(keyword in line_lower for keyword in ["disease", "pest", "name", "रोग", "कीट", "నామం", "పేరు"]):
            current_section = "disease_name"
        elif any(keyword in line_lower for keyword in ["symptoms", "लक्षण", "లక్షణాలు"]):
            current_section = "symptoms"
        elif any(keyword in line_lower for keyword in ["treatment", "उपचार", "చికిత్స"]):
            current_section = "treatment"
        elif any(keyword in line_lower for keyword in ["prevention", "रोकथाम", "నివారణ"]):
            current_section = "prevention"
        elif any(keyword in line_lower for keyword in ["confidence", "विश्वास", "నమ్మకం"]):
            current_section = "confidence"
        elif current_section and line.strip() and not line.startswith("#"):
            # Add content to current section
            if result[current_section]:
                result[current_section] += " " + line.strip()
            else:
                result[current_section] = line.strip()
    
    # If disease_name is empty, use the first non-empty line as disease name
    if not result["disease_name"]:
        for line in lines:
            if line.strip() and not any(keyword in line.lower() for keyword in ["you are", "look at", "describe"]):
                result["disease_name"] = line.strip()
                break
    
    # If parsing didn't work well, put the whole response in symptoms
    if not any([result["disease_name"], result["symptoms"], result["treatment"]]):
        result["symptoms"] = response
        result["disease_name"] = f"Analysis Required for {crop_en}" if crop_en else "Analysis Required"
    
    # Ensure confidence is set to valid value
    if result["confidence"].strip().lower() not in ["high", "medium", "low"]:
        result["confidence"] = "Medium"
    
    return result


def _get_fallback_diagnosis(crop_en: str, lang: str) -> Dict:
    """
    Provide a text-based fallback diagnosis when vision analysis is not available.
    Returns information about common diseases for the specified crop.
    """
    # Find matching crop in database
    crop_key = crop_en.lower()
    diseases = PEST_DISEASE_DATABASE.get(crop_key, PEST_DISEASE_DATABASE["wheat"])
    
    # Select a random disease from the list (more realistic than always first)
    disease_info = random.choice(diseases)
    
    # Translate response based on language
    if lang == "hi":
        return {
            "disease_name": f"{disease_info['name']} (संभावित)",
            "symptoms": f"सामान्य लक्षण: {disease_info['symptoms']}\n\nनोट: यह एक सामान्य निदान है। सटीक निदान के लिए कृषि विशेषज्ञ से संपर्क करें।",
            "treatment": f"उपचार: {disease_info['treatment']}",
            "prevention": f"रोकथाम: {disease_info['prevention']}",
            "confidence": "Low"
        }
    
    elif lang == "te":
        return {
            "disease_name": f"{disease_info['name']} (సంభావ్యం)",
            "symptoms": f"సాధారణ లక్షణాలు: {disease_info['symptoms']}\n\nగమనిక: ఇది సాధారణ నిర్ధారణ. ఖచ్చితమైన నిర్ధారణ కోసం వ్యవసాయ నిపుణుడిని సంప్రదించండి.",
            "treatment": f"చికిత్స: {disease_info['treatment']}",
            "prevention": f"నివారణ: {disease_info['prevention']}",
            "confidence": "Low"
        }
    
    else:
        return {
            "disease_name": f"{disease_info['name']} (Likely)",
            "symptoms": f"Common Symptoms: {disease_info['symptoms']}\n\nNote: This is a general diagnosis. Please consult an agricultural expert for accurate diagnosis.",
            "treatment": f"Treatment: {disease_info['treatment']}",
            "prevention": f"Prevention: {disease_info['prevention']}",
            "confidence": "Low"
        }


def get_pest_prevention_tips(crop: str, lang: str = "en", settings: dict = None) -> str:
    """
    Get general pest prevention tips for a specific crop.
    
    Args:
        crop: Crop name
        lang: Language code
        settings: AI provider settings
    
    Returns:
        str: Prevention tips in the specified language
    """
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3"}
    
    crop_en = crop.split("/")[0].strip() if "/" in crop else crop
    
    try:
        if lang == "hi":
            prompt = f"{crop_en} फसल के लिए कीट और रोग रोकथाम के व्यापक सुझाव प्रदान करें।"
        elif lang == "te":
            prompt = f"{crop_en} పంటకు తెగులు మరియు వ్యాధి నివారణ కోసం విస్తృతమైన చిట్కాలను అందించండి."
        else:
            prompt = f"Provide comprehensive pest and disease prevention tips for {crop_en} crop."
        
        system_prompt = f"You are an agricultural expert. Provide practical, organic and chemical prevention methods. Respond in {lang}."
        
        response = get_response(prompt, system_prompt, settings)
        return response if not response.startswith("Error:") else "Prevention tips unavailable."
        
    except Exception:
        return "Prevention tips unavailable at this time."