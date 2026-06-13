"""
Kisaan Mitra - AI-powered multilingual farmer assistant
Main application entry point
"""

import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from config import COMMON_CROPS, OLLAMA_MODELS, CLOUD_MODELS, SUPPORTED_LANGUAGES, INDIAN_STATES
import streamlit as st
from i18n_utils import init_language, t, set_language, get_language_name

PAGE_HOME = "home"
PAGE_CROP_ADVISOR = "crop_advisor"
PAGE_WEATHER = "weather"
PAGE_MANDI_PRICES = "mandi_prices"
PAGE_PEST_DIAGNOSIS = "pest_diagnosis"
PAGE_SCHEMES = "schemes"

PROVIDER_OLLAMA = "ollama"
PROVIDER_CLOUD = "cloud"


def safe_option_index(options, selected_value, default_index=0):
    try:
        return options.index(selected_value)
    except ValueError:
        return default_index


# Page configuration
st.set_page_config(
    page_title="Kisaan Mitra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for agricultural theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2d5a27;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4a7c59;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #f0f9e8 0%, #c8e6c9 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 2px solid #81c784;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .top-nav {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        justify-content: center;
        margin: 0.5rem 0 1.5rem 0;
    }
    .top-nav button {
        border: 1px solid #b9d9b8 !important;
        background: #f5fbf3 !important;
        color: #2d5a27 !important;
        border-radius: 999px !important;
        padding: 0.45rem 1rem !important;
        font-weight: 600 !important;
    }
    .top-nav button:hover {
        background: #e6f5e4 !important;
        border-color: #7bbf76 !important;
    }
    .top-nav button[kind="primary"] {
        background: #4CAF50 !important;
        color: white !important;
        border-color: #4CAF50 !important;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNavItems"] {
        display: none !important;
    }
    /* Sidebar Container - Ensure Visibility */
    section[data-testid="stSidebar"] {
        display: block !important;
        width: 300px !important;
        background: linear-gradient(180deg, #f5fbf3 0%, #e8f5e9 100%) !important;
        border-right: 3px solid #4CAF50 !important;
        min-height: 100vh !important;
        padding: 1rem !important;
    }
    [data-testid="stSidebar"] {
        display: block !important;
        background: linear-gradient(180deg, #f5fbf3 0%, #e8f5e9 100%) !important;
        border-right: 3px solid #4CAF50 !important;
    }
    [data-testid="stSidebar"] > div {
        display: block !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        margin: 1rem auto !important;
        display: block !important;
        text-align: center !important;
    }
    [data-testid="stSidebar"] h1 {
        color: #2d5a27 !important;
        font-size: 1.6rem !important;
        text-align: center !important;
        margin: 0.5rem 0 1rem 0 !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] h2 {
        color: #2d5a27 !important;
        font-size: 1rem !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
        text-align: left !important;
        font-weight: 600 !important;
    }
    /* Sidebar Navigation Buttons */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #ffffff 0%, #f5fbf3 100%) !important;
        color: #2d5a27 !important;
        border: 2px solid #81c784 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
        margin: 0.5rem 0 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%) !important;
        color: white !important;
        border-color: #2d5a27 !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize language settings
init_language()

# Initialize AI settings if not present
if "settings" not in st.session_state:
    st.session_state.settings = {
        "provider": PROVIDER_OLLAMA,
        "model": OLLAMA_MODELS[0],
        "api_key": ""
    }

if st.session_state.settings.get("provider") == PROVIDER_OLLAMA:
    st.session_state.settings["model"] = OLLAMA_MODELS[0]
    st.session_state["ollama_model"] = OLLAMA_MODELS[0]

# Initialize current_page if not present
if "current_page" not in st.session_state:
    st.session_state["current_page"] = PAGE_HOME

# Initialize floating chat widget state
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_input_counter" not in st.session_state:
    st.session_state.chat_input_counter = 0

# Sidebar configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/7408/7408750.png", width=80)
    st.title(t("app_title"))

    # Language selector
    st.subheader(t("sidebar_language"))
    language_options = [get_language_name(lang) for lang in SUPPORTED_LANGUAGES]
    selected_language_name = st.selectbox(
        "Select Language",
        options=language_options,
        index=SUPPORTED_LANGUAGES.index(st.session_state.lang),
        key="language_selector"
    )

    selected_lang_code = SUPPORTED_LANGUAGES[language_options.index(selected_language_name)]
    if selected_lang_code != st.session_state.lang:
        set_language(selected_lang_code)

    st.divider()

    # AI Provider selection
    st.subheader(t("sidebar_ai_provider"))

    provider = st.radio(
        "Select AI Provider",
        options=[t("provider_local"), t("provider_cloud")],
        index=0 if st.session_state.settings["provider"] == PROVIDER_OLLAMA else 1,
        horizontal=False
    )

    provider_key = PROVIDER_CLOUD if provider == t("provider_cloud") else PROVIDER_OLLAMA
    st.session_state.settings["provider"] = provider_key

    if provider_key == PROVIDER_OLLAMA:
        st.selectbox(
            t("sidebar_ollama_model"),
            options=OLLAMA_MODELS,
            index=safe_option_index(OLLAMA_MODELS, st.session_state.settings.get("model", "llama3")),
            key="ollama_model_v2"
        )
        st.session_state.settings["model"] = st.session_state.ollama_model_v2
    else:
        st.selectbox(
            t("sidebar_cloud_model"),
            options=CLOUD_MODELS,
            index=safe_option_index(CLOUD_MODELS, st.session_state.settings.get("model", "gpt-4o"), 0),
            key="cloud_model"
        )
        st.session_state.settings["model"] = st.session_state.cloud_model

        api_key = st.text_input(
            t("sidebar_api_key"),
            type="password",
            placeholder=t("sidebar_api_key_placeholder"),
            key="api_key_input"
        )
        st.session_state.settings["api_key"] = api_key

    st.divider()

    # Navigation menu in sidebar
    st.subheader("📍 Navigation")
    
    nav_options = [
        (PAGE_HOME, "🏠 Home"),
        (PAGE_CROP_ADVISOR, "🌱 Crop Advisor"),
        (PAGE_WEATHER, "🌤️ Weather"),
        (PAGE_MANDI_PRICES, "🏪 Mandi Prices"),
        (PAGE_PEST_DIAGNOSIS, "🔍 Pest Diagnosis"),
        (PAGE_SCHEMES, "📋 Govt Schemes")
    ]
    
    for page_id, label in nav_options:
        if st.button(label, use_container_width=True, key=f"sidebar_nav_{page_id}"):
            st.session_state["current_page"] = page_id
            st.rerun()

# Main content area
current_page = st.session_state["current_page"]

if current_page == PAGE_HOME:
    st.markdown(f'<h1 class="main-header">{t("app_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{t("app_subtitle")}</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="success-box">
        <h3>🌾 {t("home_welcome")}</h3>
        <p>{t("home_description")}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='color: #2d5a27;'>{t('home_features_title')}</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🌱 Crop Advisor</h3>
            <p>Get expert advice on crop selection, sowing, fertilizers, and harvest timing</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🌤️ Weather Forecast</h3>
            <p>7-day weather forecast with AI-powered farming recommendations</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🏪 Mandi Prices</h3>
            <p>Real-time market prices and AI advice on when and where to sell</p>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Pest Diagnosis</h3>
            <p>Upload crop images for AI-powered disease and pest identification</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Govt Schemes</h3>
            <p>Discover relevant government schemes and subsidies for farmers</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="feature-card">
            <h3>🌿 Multilingual</h3>
            <p>Available in English, Hindi, and Telugu for better accessibility</p>
        </div>
        """, unsafe_allow_html=True)

elif current_page == PAGE_CROP_ADVISOR:
    from pages.crop_advisor_page import show_crop_advisor
    show_crop_advisor(t, COMMON_CROPS, st.session_state.settings)

elif current_page == PAGE_WEATHER:
    from pages.weather_page import show_weather
    show_weather(t, COMMON_CROPS, st.session_state.settings)

elif current_page == PAGE_MANDI_PRICES:
    from pages.mandi_prices_page import show_mandi_prices
    show_mandi_prices(t, COMMON_CROPS, INDIAN_STATES, st.session_state.settings)

elif current_page == PAGE_PEST_DIAGNOSIS:
    from pages.pest_diagnosis_page import show_pest_diagnosis
    show_pest_diagnosis(t, COMMON_CROPS, st.session_state.settings)

elif current_page == PAGE_SCHEMES:
    from pages.scheme_finder_page import show_schemes
    show_schemes(t, COMMON_CROPS, INDIAN_STATES, st.session_state.settings)


# ============================================================
# Floating Chat Widget (Pure Streamlit widgets, CSS-positioned)
# ============================================================
def render_floating_widget():
    """Render a floating chat widget at bottom-right using real Streamlit widgets."""

    try:
        from modules.chatbot import get_chatbot_response, format_chat_message, validate_message
    except ModuleNotFoundError as e:
        st.error(f"Chat module not available: {str(e)}. Please ensure all dependencies are installed.")
        return

    st.markdown("""
    <style>
        .floating-chat-anchor {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            width: 520px;
        }
        .floating-chat-anchor .chat-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 40px rgba(0,0,0,0.16);
            overflow: hidden;
            margin-bottom: 10px;
            padding-bottom: 0.5rem;
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .chat-header {
            background: linear-gradient(135deg, #2d5a27 0%, #4CAF50 100%);
            color: white;
            padding: 1rem 1.2rem;
            font-weight: 600;
            font-size: 1.1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-messages {
            max-height: 480px;
            overflow-y: auto;
            padding: 1rem;
            background: #f5f5f5;
        }
        .message { display: flex; margin-bottom: 0.6rem; }
        .message.user { justify-content: flex-end; }
        .message-bubble {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 14px;
            font-size: 0.95rem;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .message.user .message-bubble {
            background: #4CAF50; color: white; border-radius: 14px 14px 0 14px;
        }
        .message.assistant .message-bubble {
            background: #e8f5e9; color: #333; border-radius: 14px 14px 14px 0;
            white-space: pre-wrap;
        }
        .chat-welcome {
            padding: 2rem; text-align: center; color: #666;
        }
        .chat-welcome-emoji { font-size: 3rem; }
        .chat-welcome-title { font-size: 1.15rem; font-weight: 600; margin: 0.6rem 0; }
        .chat-welcome-text { font-size: 0.9rem; margin: 0.3rem 0; }

        .floating-chat-anchor .stTextInput input {
            border-radius: 20px !important;
            font-size: 0.95rem !important;
        }
        .floating-chat-anchor .stButton button {
            border-radius: 20px !important;
            background: #4CAF50 !important;
            font-size: 1rem !important;
        }
        
        /* Floating FAB button when chat is closed */
        .floating-chat-anchor .stButton button[key="fab_toggle_closed"] {
            width: 70px !important;
            height: 70px !important;
            border-radius: 50% !important;
            padding: 0 !important;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem !important;
            background: linear-gradient(135deg, #2d5a27 0%, #4CAF50 100%) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }
        
        .floating-chat-anchor .stButton button[key="fab_toggle_closed"]:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
        }
        
        /* Scrollbar styling */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="floating-chat-anchor">', unsafe_allow_html=True)

    if st.session_state.chat_open:
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)

        hcol1, hcol2 = st.columns([5, 1])
        with hcol1:
            st.markdown('<div class="chat-header">💬 Kisaan Mitra</div>', unsafe_allow_html=True)
        with hcol2:
            if st.button("✕", key="chat_close_btn"):
                st.session_state.chat_open = False
                st.rerun()

        messages_html = ""
        if not st.session_state.chat_history:
            messages_html = (
                '<div class="chat-welcome">'
                '<div class="chat-welcome-emoji">🌾</div>'
                '<div class="chat-welcome-title">नमस्ते Namaste!</div>'
                '<div class="chat-welcome-text">Ask me anything about farming</div>'
                '<div class="chat-welcome-text">English • हिंदी • తెలుగు</div>'
                '</div>'
            )
        else:
            for msg in st.session_state.chat_history:
                msg_class = "user" if msg["role"] == "user" else "assistant"
                msg_icon = "👨‍🌾" if msg["role"] == "user" else "🤖"
                msg_content = msg["content"].replace('<', '&lt;').replace('>', '&gt;')
                messages_html += (
                    '<div class="message ' + msg_class + '">'
                    '<div class="message-bubble">' + msg_icon + ' ' + msg_content + '</div>'
                    '</div>'
                )

        st.markdown('<div class="chat-messages">' + messages_html + '</div>', unsafe_allow_html=True)

        icol1, icol2 = st.columns([5, 1])
        with icol1:
            user_text = st.text_input(
                "Message",
                key=f"floating_chat_input_{st.session_state.chat_input_counter}",
                placeholder="Ask about farming, crops, weather...",
                label_visibility="collapsed"
            )
        with icol2:
            send_clicked = st.button("📤", key="floating_chat_send")

        st.markdown('</div>', unsafe_allow_html=True)

        if send_clicked and user_text and user_text.strip():
            user_input = user_text.strip()
            is_valid, error_msg = validate_message(user_input)

            if is_valid:
                user_message = format_chat_message("user", user_input)
                st.session_state.chat_history.append(user_message)

                try:
                    llm_settings = {
                        "provider": st.session_state.settings.get("provider", "ollama"),
                        "model": st.session_state.settings.get("model", "llama3.2:1b"),
                        "api_key": st.session_state.settings.get("api_key", "")
                    }

                    with st.spinner("🤔 Kisaan Mitra is thinking..."):
                        response = get_chatbot_response(
                            user_message=user_input,
                            chat_history=st.session_state.chat_history[:-1],
                            settings=llm_settings
                        )

                    assistant_message = format_chat_message("assistant", response)
                    st.session_state.chat_history.append(assistant_message)

                except Exception as e:
                    error_response = str(e)
                    if "Connection refused" in error_response or "Ollama" in error_response or "refused" in error_response.lower():
                        error_response = "⚠️ Cannot connect to Ollama. Please:\n1. Start Ollama locally, OR\n2. Switch to Cloud (BYOK) in the sidebar"
                    elif "api_key" in error_response.lower() or "key" in error_response.lower():
                        error_response = "⚠️ Invalid API key. Please check your Cloud API key in the sidebar."
                    elif not error_response:
                        error_response = "❌ An unknown error occurred. Please try again."
                    else:
                        error_response = f"❌ Error: {error_response}"

                    error_msg_obj = format_chat_message("assistant", error_response)
                    st.session_state.chat_history.append(error_msg_obj)

                st.session_state.chat_input_counter += 1
                st.rerun()

    else:
        if st.button("💬", key="fab_toggle_closed", help="Open Kisaan Mitra Chat"):
            st.session_state.chat_open = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


render_floating_widget()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🌾 Kisaan Mitra - Empowering Farmers with AI 🌾</p>
        <p style='font-size: 0.8rem;'>Built with ❤️ for Indian Farmers</p>
    </div>
    """,
    unsafe_allow_html=True
)