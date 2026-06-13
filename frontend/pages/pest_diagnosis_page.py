"""
Pest Diagnosis page - AI-powered pest and disease identification from crop images.
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from modules.pest_diagnosis import diagnose_pest
import streamlit as st
from PIL import Image


def show_pest_diagnosis(t, common_crops, settings):
    """
    Display the Pest Diagnosis page.
    
    Args:
        t: Translation function
        common_crops: List of common crops from config
        settings: AI provider settings dictionary
    """
    st.title(t("pest_title"))
    st.write(t("pest_description"))
    
    # Create form for pest diagnosis
    with st.form("pest_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                t("pest_upload_label"),
                type=["jpg", "jpeg", "png"],
                help=t("pest_upload_help")
            )
        
        with col2:
            crop = st.selectbox(
                t("pest_crop_label"),
                options=common_crops
            )
        
        submitted = st.form_submit_button(
            t("pest_submit"),
            use_container_width=True
        )
    
    if submitted:
        if uploaded_file is None:
            st.error(t("pest_no_image"))
        else:
            with st.spinner(t("loading")):
                try:
                    # Get current language from session state
                    lang = st.session_state.get("lang", "en")
                    
                    # Read and display the uploaded image
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded crop image", use_container_width=True)
                    
                    # Read image bytes for diagnosis
                    image_bytes = uploaded_file.getvalue()
                    
                    # Perform diagnosis
                    result = diagnose_pest(
                        image_bytes=image_bytes,
                        crop=crop,
                        lang=lang,
                        settings=settings
                    )
                    
                    if result:
                        st.success(t("success"))
                        
                        # Display results in 4 sections
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### {t('pest_disease_name')}")
                            st.info(result.get("disease_name", "Unknown"))
                            
                            st.markdown(f"### {t('pest_symptoms')}")
                            st.write(result.get("symptoms", "No symptoms information available"))
                        
                        with col2:
                            st.markdown(f"### {t('pest_treatment')}")
                            st.write(result.get("treatment", "No treatment information available"))
                            
                            st.markdown(f"### {t('pest_prevention')}")
                            st.write(result.get("prevention", "No prevention information available"))
                        
                        # Additional recommendations
                        with st.expander("🌿 Additional Recommendations"):
                            st.markdown("""
                            #### General Tips:
                            - Regularly inspect your crops for early signs of disease
                            - Practice crop rotation to break pest cycles
                            - Maintain proper spacing between plants for air circulation
                            - Remove and destroy infected plant parts immediately
                            - Consult local agricultural experts for region-specific advice
                            """)
                    
                except Exception as e:
                    st.error(f"{t('error_generic')}: {str(e)}")
    
    # Information section
    with st.expander("ℹ️ How to use Pest Diagnosis"):
        st.markdown("""
        ### Taking Good Photos for Diagnosis:
        
        1. **Close-up shots**: Get close to the affected area
        2. **Good lighting**: Use natural daylight when possible
        3. **Multiple angles**: Take photos from different angles
        4. **Clear focus**: Ensure the image is not blurry
        5. **Show symptoms**: Focus on the damaged or diseased parts
        
        ### What to photograph:
        - **Leaves**: Both top and bottom surfaces
        - **Stems**: Any discoloration or lesions
        - **Fruits/Flowers**: Spots, rot, or deformities
        - **Overall plant**: To show the pattern of damage
        
        ### Limitations:
        - AI diagnosis is for guidance only
        - Always confirm with local agricultural experts
        - Some diseases may look similar and require lab testing
        """)