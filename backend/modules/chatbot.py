"""
Chatbot module - Conversational AI assistant for general farm questions.
Auto-detects language and provides comprehensive agricultural guidance.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.llm_client import get_response, get_claude_response
from config import SUPPORTED_LANGUAGES


def detect_language(text: str) -> str:
    """
    Detect language from user input based on Unicode ranges.
    """
    if not text or not text.strip():
        return "en"
    
    devanagari_count = 0
    telugu_count = 0
    
    for char in text:
        code_point = ord(char)
        
        # Devanagari range for Hindi
        if 0x0900 <= code_point <= 0x097F:
            devanagari_count += 1
        # Telugu range
        elif 0x0C00 <= code_point <= 0x0C7F:
            telugu_count += 1
    
    if telugu_count > 0:
        return "te"
    if devanagari_count > 0:
        return "hi"
    return "en"


# Comprehensive system prompts for general farming questions
SYSTEM_PROMPTS = {
    "en": """You are Kisaan Mitra, an expert agricultural AI assistant for Indian farmers.

YOUR ROLE:
- Answer ALL types of farming questions: crops, soil, water, weather, pests, market, government schemes
- Provide PRACTICAL advice specific to Indian agriculture and climate
- For questions about best crops for a season, ALWAYS provide at least 3-5 specific crop recommendations with WHY each is good
- For market questions, mention realistic prices and best selling times
- For government schemes, list specific programs farmers can access
- For pest problems, suggest both prevention and treatment methods
- For soil issues, recommend practical solutions with locally available materials

CRITICAL: 
- Be conversational and helpful, not just informative
- Answer questions directly without unnecessary preamble
- Provide actionable, farmer-friendly advice
- Use simple language that farmers easily understand
- For questions you cannot fully answer, suggest consulting local agricultural experts

RESPONSE FORMAT:
- 2-3 clear paragraphs for comprehensive questions
- 1 paragraph for quick questions
- Use bullet points for lists when appropriate
- Include specific crop names, prices, and timeframes when relevant""",

    "hi": """आप किसान मित्र हैं, भारतीय किसानों के लिए एक विशेषज्ञ कृषि AI सहायक।

आपका रोल:
- सभी प्रकार के खेती के सवालों का जवाब दें: फसलें, मिट्टी, पानी, मौसम, कीट, बाजार, सरकारी योजनाएं
- भारतीय कृषि और जलवायु के लिए व्यावहारिक सलाह दें
- किसी मौसम के लिए सर्वश्रेष्ठ फसलें के सवालों के लिए, हमेशा 3-5 विशिष्ट फसलों की सिफारिशें करें
- बाजार के सवालों के लिए यथार्थवादी कीमतें और बेचने का सर्वश्रेष्ठ समय बताएं
- सरकारी योजनाओं के लिए, किसानों के लिए उपलब्ध विशिष्ट कार्यक्रम सूचीबद्ध करें
- कीट समस्याओं के लिए रोकथाम और उपचार दोनों विधियां सुझाएं
- मिट्टी की समस्याओं के लिए, स्थानीय रूप से उपलब्ध सामग्री से व्यावहारिक समाधान की सिफारिश करें

महत्वपूर्ण:
- संवादात्मक और मददगार बनें, केवल जानकारीपूर्ण नहीं
- सवालों का सीधे जवाब दें
- कार्यान्वयन योग्य, किसान-अनुकूल सलाह प्रदान करें
- सरल भाषा का उपयोग करें
- जो आप पूरी तरह से नहीं जानते, स्थानीय कृषि विशेषज्ञों से परामर्श लेने का सुझाव दें

प्रतिक्रिया प्रारूप:
- व्यापक सवालों के लिए 2-3 स्पष्ट पैराग्राफ
- त्वरित सवालों के लिए 1 पैराग्राफ
- जब उपयुक्त हो तो बुलेट पॉइंट का उपयोग करें
- विशिष्ट फसल के नाम, कीमतें, और समय सीमा शामिल करें""",

    "te": """మీరు కిసాన్ మిత్ర, భారతీయ రైతుల కోసం ఒక నిపుణుడైన వ్యవసాయ AI సహాయకుడు.

మీ పాత్ర:
- అన్ని రకాల పంటల సంబంధిత ప్రశ్నలకు సమాధానం ఇవ్వండి: పంటలు, నేల, నీరు, వాతావరణం, తెగుళ్లు, మార్కెట్, ప్రభుత్వ పథకాలు
- భారతీయ వ్యవసాయానికి సంబంధించిన ఆచరణాత్మక సలహా ఇవ్వండి
- ఒక సీజన్ కోసం ఉత్తమ పంటల గురించిన ప్రశ్నలకు, కనీసం 3-5 నిర్దిష్ట పంట సిఫారసులు ఇవ్వండి
- మార్కెట్ ప్రశ్నల కోసం, వాస్తవిక ధరలు మరియు సరైన విక్రయ సమయం చెప్పండి
- ప్రభుత్వ పథకాల కోసం, రైతులకు అందుబాటులో ఉన్న నిర్దిష్ట కార్యక్రమాలను జాబితా చేయండి

నిర్ణయాత్మక:
- సంభాషణాత్మకమైనది మరియు సహాయకమైనది, కేవలం సమాచారాత్మకమైనది కాదు
- ప్రశ్నలకు నేరుగా సమాధానం ఇవ్వండి
- సెయ్యదగ్గ, రైతు-స్నేహపూర్వక సలహా ఇవ్వండి
- సరళ భాష ఉపయోగించండి
- గూढ్లను కీర్తించండి""",
}

# Farming knowledge base for quick reference
FARMING_KNOWLEDGE = {
    "winter_crops": [
        "Wheat - Highest yield crop, sown Oct-Dec, harvest Mar-Apr",
        "Chickpea - High protein, good for soil, sown Oct-Nov",
        "Mustard - Oil crop, good market price, sown Oct-Nov",
        "Barley - Drought tolerant, sown Oct-Dec",
        "Lentil - Nutritious, improves soil nitrogen, sown Oct-Nov"
    ],
    "summer_crops": [
        "Rice - Main summer crop, sown Jun-Jul, needs water",
        "Maize - Quick maturity (90-120 days), sown Apr-Jul",
        "Groundnut - Good market demand, sown May-Jun",
        "Sesame - Oil crop, low water needs, sown May-Jun",
        "Cotton - Long duration, sown May-Jun, good prices"
    ],
    "monsoon_crops": [
        "Rice - Primary monsoon crop, sown Jun-Aug",
        "Soybean - New option, good prices, sown Jun-Jul",
        "Maize - Fits monsoon season, sown Jun-Jul",
        "Green gram - Legume, quick crop, sown Jun-Jul",
        "Black gram - Legume, good market, sown Jun-Jul"
    ],
    "irrigation_tips": [
        "Drip irrigation saves 40-60% water vs flood irrigation",
        "Use mulching to reduce water evaporation",
        "Early morning irrigation is more efficient",
        "Check soil moisture before irrigating",
        "Use micro-sprinklers for vegetables"
    ],
    "pest_control": [
        "Use neem oil spray for 80% of common pests",
        "Release ladybugs for aphid control",
        "Use IPM (Integrated Pest Management) for sustainable farming",
        "Set pheromone traps for early pest detection",
        "Proper crop rotation prevents pest buildup"
    ]
}


def get_chatbot_response(
    user_message: str,
    chat_history: list = None,
    settings: dict = None
) -> str:
    """
    Get a chatbot response for general farming questions.
    
    Args:
        user_message: The user's input question
        chat_history: Previous conversation for context
        settings: AI provider settings
    
    Returns:
        str: Conversational response in detected language
    """
    if chat_history is None:
        chat_history = []
    
    if settings is None:
        settings = {"provider": "ollama", "model": "llama3.2:1b"}
    
    # Auto-detect language
    detected_lang = detect_language(user_message)
    if detected_lang not in SUPPORTED_LANGUAGES:
        detected_lang = "en"
    
    system_prompt = SYSTEM_PROMPTS.get(detected_lang, SYSTEM_PROMPTS["en"])
    
    # Build context from recent chat history
    context = ""
    if chat_history:
        recent = chat_history[-5:]  # Last 5 messages
        for msg in recent:
            context += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
    
    # Construct full prompt with context
    full_prompt = user_message
    if context:
        full_prompt = f"Previous conversation:\n{context}\nNew question: {user_message}"
    
    try:
        # Try Ollama first
        response = get_response(full_prompt, system_prompt, settings)
        
        if response and not response.startswith("Error"):
            return response
        
        # Ollama failed - try Claude fallback
        print("📱 Using Claude API for general question...")
        claude_response = get_claude_response(full_prompt, system_prompt)
        
        if claude_response and not claude_response.startswith("Error"):
            return claude_response
        
        # Both failed - return knowledge base summary
        if "winter" in user_message.lower() or "season" in user_message.lower():
            return "\n".join(FARMING_KNOWLEDGE.get("winter_crops", []))
        
        return "I'm having difficulty answering right now. Please try again or contact local agricultural experts."
        
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return "An error occurred. Please try again."


def format_chat_message(role: str, content: str) -> dict:
    """Format a chat message for storage."""
    return {
        "role": role,
        "content": content,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


def validate_message(user_input: str) -> tuple:
    """
    Validate user message before sending to chatbot.
    
    Args:
        user_input: The user's input message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not user_input or not user_input.strip():
        return False, "Message cannot be empty"
    
    if len(user_input) > 5000:
        return False, "Message is too long (max 5000 characters)"
    
    # Message is valid
    return True, ""
