"""
Internationalization (i18n) utilities for Kisaan Mitra frontend.
Handles language switching and translation loading.
"""

import json
import os
import streamlit as st

# Path to translation files
I18N_DIR = os.path.join(os.path.dirname(__file__), "i18n")

def load_translations(lang: str = "en") -> dict:
    """
    Load translations from JSON file for the specified language.
    
    Args:
        lang: Language code ("en", "hi", or "te")
    
    Returns:
        dict: Dictionary of translation keys and their translated values
    """
    translation_file = os.path.join(I18N_DIR, f"{lang}.json")
    
    try:
        with open(translation_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
        return translations
    except FileNotFoundError:
        # Fallback to English if translation file not found
        if lang != "en":
            st.warning(f"Translation file for '{lang}' not found. Using English as fallback.")
            return load_translations("en")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"Error parsing translation file: {e}")
        return {}


def t(key: str) -> str:
    """
    Translate a key to the current language.
    
    Args:
        key: Translation key
    
    Returns:
        str: Translated text, or the key itself if translation not found
    """
    # Get translations from session state
    translations = st.session_state.get("translations", {})
    
    # Return translated text or fallback to key
    return translations.get(key, key)


def init_language() -> None:
    """
    Initialize language settings in session state.
    Sets default language to English if not already set.
    """
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    
    if "translations" not in st.session_state:
        st.session_state.translations = load_translations(st.session_state.lang)


def set_language(lang: str) -> None:
    """
    Change the application language and reload translations.
    
    Args:
        lang: New language code ("en", "hi", or "te")
    """
    st.session_state.lang = lang
    st.session_state.translations = load_translations(lang)
    # Rerun the app to apply language change
    st.rerun()


def get_language_name(lang: str) -> str:
    """
    Get the display name for a language code.
    
    Args:
        lang: Language code
    
    Returns:
        str: Language name in its native script
    """
    names = {
        "en": "English",
        "hi": "हिंदी",
        "te": "తెలుగు"
    }
    return names.get(lang, lang)