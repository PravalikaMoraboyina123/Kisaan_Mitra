"""
Unified LLM client using litellm for both local Ollama and cloud BYOK providers.
Includes Claude API fallback for production reliability.
"""

import litellm
import os
from typing import Dict


def _offline_crop_advice(system_prompt: str, prompt: str, model: str) -> str:
    """Return a structured fallback response when local Ollama is unavailable."""
    crop_name = "this crop"
    for marker in ["Crop:", "Crop -", "Crop is"]:
        if marker in prompt:
            fragment = prompt.split(marker, 1)[1].strip().splitlines()[0]
            if fragment:
                crop_name = fragment
            break

    return f"""Seasonal Plan
Local AI is currently unavailable, so this is a practical fallback guide for {crop_name}. Prepare your field, verify seed quality, and match sowing with local weather.

Fertilizer Schedule
Use compost or well-decomposed FYM before sowing. Apply nitrogen, phosphorus, and potassium in split doses based on soil test results.

Pest Watch
Watch for early signs of sucking pests, fungal spots, and moisture-related diseases. Inspect the crop regularly, especially after rainfall.

Harvest Window
Harvest when the crop reaches full maturity and grain or fruit quality is stable. Avoid harvesting during wet conditions.

Tips
Keep irrigation balanced, remove weeds early, and prefer a soil test before adding extra fertilizer.
"""


def get_response(
    prompt: str,
    system_prompt: str,
    settings: Dict[str, str]
) -> str:
    """
    Get a text response from an LLM based on the selected provider.
    
    Args:
        prompt: The user's input prompt
        system_prompt: The system instruction for the AI
        settings: Dictionary containing provider settings:
            - provider: "ollama" or "cloud"
            - model: The model name to use
            - api_key: API key for cloud providers (optional for Ollama)
    
    Returns:
        str: The AI-generated response, or an error message on failure
    """
    try:
        provider = settings.get("provider", "ollama")
        model = settings.get("model", "llama3")
        api_key = settings.get("api_key", "")
        
        if provider == "ollama":
            # Local Ollama inference
            model_name = f"ollama/{model}"
            api_base = "http://localhost:11434"
            api_key = "ollama"  # litellm requires a dummy key for Ollama
        elif provider == "cloud":
            # Cloud provider with BYOK
            model_name = model
            api_base = None
            if not api_key:
                return "Error: API key is required for cloud provider. Please provide your API key in the sidebar."
        else:
            return f"Error: Unknown provider '{provider}'. Use 'ollama' or 'cloud'."
        
        # Prepare messages for litellm
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Call litellm completion with optimized parameters for crop-specific responses
        response = litellm.completion(
            model=model_name,
            messages=messages,
            api_key=api_key,
            api_base=api_base if api_base else None,
            temperature=0.8,  # Slightly higher for variation between crops
            max_tokens=2000,  # Increased for detailed crop-specific responses
            timeout=60
        )
        
        # Extract and return the response text
        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No response received from the AI model."
            
    except litellm.exceptions.APIError as e:
        return f"API Error: {str(e)}"
    except litellm.exceptions.AuthenticationError:
        return "Authentication Error: Invalid API key or authentication failed."
    except litellm.exceptions.BadRequestError as e:
        return f"Bad Request: {str(e)}"
    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg:
            if provider == "ollama":
                return _offline_crop_advice(system_prompt, prompt, model)
            return "Error: Cannot connect to the selected AI provider. Please check your connection or API key."
        elif "not found" in error_msg or "model" in error_msg:
            return f"Error: Model '{settings.get('model', '')}' not found. Please select a different model."
        return f"Error: {str(e)}"


def get_vision_response(
    prompt: str,
    image_base64: str,
    settings: Dict[str, str]
) -> str:
    """
    Get a vision response from an LLM that supports image analysis.
    
    Args:
        prompt: The user's question about the image
        image_base64: Base64-encoded image data
        settings: Dictionary containing provider settings (same as get_response)
    
    Returns:
        str: The AI-generated response about the image, or an error message
    """
    try:
        provider = settings.get("provider", "ollama")
        model = settings.get("model", "llama3")
        api_key = settings.get("api_key", "")
        
        # Check if the model supports vision
        vision_supported_models = ["gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro", "llava"]
        
        if provider == "ollama":
            # Check if it's a vision-capable Ollama model
            if model not in vision_supported_models:
                return None  # Signal to use fallback
            model_name = f"ollama/{model}"
            api_base = "http://localhost:11434"
            api_key = "ollama"
        elif provider == "cloud":
            if model not in vision_supported_models:
                return None  # Signal to use fallback
            model_name = model
            api_base = None
            if not api_key:
                return "Error: API key is required for cloud vision analysis."
        else:
            return f"Error: Unknown provider '{provider}'."
        
        # Prepare image content
        image_url = f"data:image/jpeg;base64,{image_base64}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        
        response = litellm.completion(
            model=model_name,
            messages=messages,
            api_key=api_key,
            api_base=api_base if api_base else None,
            temperature=0.3,
            max_tokens=350,
            timeout=60
        )
        
        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No response received from the vision model."
            
    except litellm.exceptions.UnsupportedParamsError:
        return None  # Signal to use fallback
    except Exception as e:
        error_msg = str(e).lower()
        if "vision" in error_msg or "image" in error_msg:
            return None  # Signal to use fallback
        return f"Vision Error: {str(e)}"

def get_claude_response(prompt: str, system_prompt: str) -> str:
    """
    Get a response from Claude API as fallback when Ollama is unavailable.
    
    Args:
        prompt: The user's input prompt
        system_prompt: The system instruction for the AI
    
    Returns:
        str: The AI-generated response, or an error message on failure
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        if not api_key:
            return "Error: ANTHROPIC_API_KEY not set. Claude fallback unavailable."
        
        # Use litellm to call Claude
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = litellm.completion(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            api_key=api_key,
            temperature=0.7,
            max_tokens=2000,
            timeout=60
        )
        
        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No response from Claude API"
    
    except Exception as e:
        return f"Error: Claude API failed - {str(e)}"
