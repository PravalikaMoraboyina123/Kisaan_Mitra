"""
Chatbot page - Interactive conversational interface for farmers.
Supports multilingual input and output with chat history.
Floating widget positioned at bottom-right.
"""

import sys
import os
import streamlit as st
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from modules.chatbot import get_chatbot_response, format_chat_message, validate_message
from i18n_utils import t


def render_chatbot_page():
    """Render the chatbot page with floating chat widget."""
    
    # Custom CSS for floating chat widget at bottom-right
    st.markdown("""
    <style>
        /* Main page layout */
        body {
            overflow: hidden;
        }
        
        .floating-chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 420px;
            height: 700px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
            display: flex;
            flex-direction: column;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #2d5a27 0%, #4CAF50 100%);
            color: white;
            padding: 1rem;
            border-radius: 15px 15px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .chat-header-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
        }
        
        .chat-header-lang {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        
        .chat-messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background-color: #f8f9fa;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .chat-message {
            display: flex;
            margin-bottom: 0.5rem;
            animation: slideIn 0.3s ease-in-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message-user {
            justify-content: flex-end;
        }
        
        .message-user .message-content {
            background-color: #4CAF50;
            color: white;
            border-radius: 12px 12px 0 12px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .message-assistant .message-content {
            background-color: #e3f2fd;
            color: #333;
            border-radius: 12px 12px 12px 0;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .message-content {
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        
        .chat-input-section {
            padding: 1rem;
            background: white;
            border-top: 1px solid #ddd;
            border-radius: 0 0 15px 15px;
            display: flex;
            gap: 0.5rem;
        }
        
        .chat-input-box {
            flex: 1;
            padding: 0.75rem;
            border: 1.5px solid #ddd;
            border-radius: 20px;
            font-size: 0.9rem;
            font-family: inherit;
            resize: none;
            max-height: 80px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .chat-input-box:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
        }
        
        .chat-send-btn {
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        
        .chat-send-btn:hover {
            background: #45a049;
        }
        
        .chat-send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .empty-message {
            text-align: center;
            color: #999;
            padding: 2rem 1rem;
        }
        
        .controls-top {
            display: flex;
            gap: 0.5rem;
            padding: 0.75rem;
            justify-content: space-around;
            background: white;
            border-bottom: 1px solid #eee;
        }
        
        .control-btn {
            background: white;
            border: 1px solid #ddd;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        
        .control-btn:hover {
            background: #f5f5f5;
            border-color: #4CAF50;
        }
        
        .info-box {
            background: linear-gradient(135deg, #f0f9e8 0%, #c8e6c9 100%);
            border-left: 4px solid #4CAF50;
            padding: 1rem;
            margin: 1rem;
            border-radius: 8px;
        }
        
        /* Scrollbar styling */
        .chat-messages-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-messages-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .chat-messages-container::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 10px;
        }
        
        .chat-messages-container::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize chat history in session state if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "chat_thinking" not in st.session_state:
        st.session_state.chat_thinking = False
    
    # Get current language
    current_language = st.session_state.get("language", "en")
    lang_names = {"en": "English 🇬🇧", "hi": "हिंदी 🇮🇳", "te": "తెలుగు 🇮🇳"}
    lang_display = lang_names.get(current_language, "English")
    
    # Build the floating chat widget HTML
    chat_widget_html = f'''
    <div class="floating-chat-widget">
        <!-- Header -->
        <div class="chat-header">
            <h3 class="chat-header-title">💬 Kisaan Mitra</h3>
            <div class="chat-header-lang">{lang_display}</div>
        </div>
        
        <!-- Control buttons -->
        <div class="controls-top">
            <button class="control-btn" onclick="document.getElementById('clear-chat').click()">🗑️ Clear</button>
            <button class="control-btn" onclick="document.getElementById('export-chat').click()">💾 Export</button>
        </div>
        
        <!-- Chat messages -->
        <div class="chat-messages-container" id="chat-messages">
    '''
    
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                chat_widget_html += f'''
                <div class="chat-message message-user">
                    <div class="message-content">👨‍🌾 {message['content']}</div>
                </div>
                '''
            else:
                chat_widget_html += f'''
                <div class="chat-message message-assistant">
                    <div class="message-content">🤖 {message['content']}</div>
                </div>
                '''
    else:
        chat_widget_html += '''
        <div class="empty-message">
            <p style="font-size: 2rem; margin: 1rem 0;">नमस्ते! 👋</p>
            <p style="font-size: 0.9rem; margin: 0.5rem 0;">Ask about farming, crops, weather, pests & more!</p>
            <p style="font-size: 0.8rem; margin: 0.5rem 0; color: #bbb;">English • हिंदी • తెలుగు</p>
        </div>
        '''
    
    chat_widget_html += '''
        </div>
    </div>
    '''
    
    # Render the floating widget
    st.markdown(chat_widget_html, unsafe_allow_html=True)
    
    # Hidden controls section
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗑️ Clear Chat History", key="clear-chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", key="export-chat"):
            export_chat()
    
    with col3:
        stats_col = st.empty()
        if st.session_state.chat_history:
            total = len(st.session_state.chat_history)
            user_count = sum(1 for msg in st.session_state.chat_history if msg["role"] == "user")
            stats_col.metric("Messages", total)
    
    st.divider()
    
    # Main content area with info
    st.markdown("""
    <div class="info-box">
        <h3>💡 Chat Assistant Guide</h3>
        <p><strong>How to use:</strong></p>
        <ul>
            <li>Ask in your preferred language (English, हिंदी, or తెలుగు)</li>
            <li>Topics: Crops, Weather, Market Prices, Pests, Government Schemes</li>
            <li>Responses will be in the same language</li>
            <li>Use Clear to remove chat history</li>
            <li>Use Export to download conversations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Example questions
    st.markdown("### 📝 Example Questions:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌾 English:**
        - What fertilizer for wheat?
        - How to control pests?
        - Best sowing time?
        """)
    
    with col2:
        st.markdown("""
        **🇮🇳 हिंदी:**
        - गेहूं की खाद क्या है?
        - कीटों को कैसे नियंत्रित करें?
        - सर्वोत्तम बुवाई समय?
        """)
    
    with col3:
        st.markdown("""
        **🇮🇳 తెలుగు:**
        - గోధుమ కోసం సారం?
        - పీడకలను నియంత్రించు?
        - సేత సమయం?
        """)
    
    # Input section below content
    st.divider()
    st.markdown("### ✍️ Type Your Message:")
    
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_area(
            label="Message",
            placeholder=t("chatbot_input_placeholder"),
            key="user_message_input",
            disabled=st.session_state.chat_thinking,
            height=100,
            label_visibility="collapsed"
        )
    
    with col_btn:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        send_button = st.button(
            "📤 Send",
            key="send_button",
            disabled=st.session_state.chat_thinking,
            use_container_width=True
        )
    
    # Handle message submission
    if send_button and user_input:
        is_valid, error_msg = validate_message(user_input)
        if not is_valid:
            st.error(error_msg)
        else:
            user_message = format_chat_message("user", user_input)
            st.session_state.chat_history.append(user_message)
            
            st.session_state.chat_thinking = True
            
            try:
                current_language = st.session_state.get("language", "en")
                
                llm_settings = {
                    "provider": st.session_state.get("provider", "ollama"),
                    "model": st.session_state.get("model", "llama3.2:1b"),
                    "api_key": st.session_state.get("api_key", "")
                }
                
                with st.spinner(t("chatbot_thinking")):
                    response = get_chatbot_response(
                        user_message=user_input,
                        language=current_language,
                        chat_history=st.session_state.chat_history[:-1],
                        settings=llm_settings
                    )
                
                assistant_message = format_chat_message("assistant", response)
                st.session_state.chat_history.append(assistant_message)
                
                st.success("✅ Response received!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            
            finally:
                st.session_state.chat_thinking = False
                st.rerun()


def export_chat():
    """Export chat history as text."""
    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.warning(t("chatbot_no_history"))
        return
    
    # Format chat history as text
    chat_text = f"Kisaan Mitra Chat History\n"
    chat_text += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += "=" * 50 + "\n\n"
    
    for message in st.session_state.chat_history:
        role = "👨‍🌾 You" if message["role"] == "user" else "🤖 Kisaan Mitra"
        timestamp = message.get("timestamp", "")
        content = message["content"]
        
        chat_text += f"{role} ({timestamp}):\n{content}\n\n"
    
    st.download_button(
        label=t("chatbot_download_button"),
        data=chat_text,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


if __name__ == "__main__":
    render_chatbot_page()


if __name__ == "__main__":
    render_chatbot_page()
