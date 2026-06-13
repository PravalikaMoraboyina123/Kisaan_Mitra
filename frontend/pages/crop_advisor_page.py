"""
Crop Advisor page - Provides AI-powered crop recommendations and farming advice.
"""

import sys
import os
import importlib
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

import streamlit as st


def _get_crop_advice(*args, **kwargs):
    module = importlib.import_module("modules.crop_advisor")
    return module.get_crop_advice(*args, **kwargs)


def _fallback_crop_advice(crop: str) -> dict:
    return {
        "seasonal_plan": f"Local AI is currently unavailable, so this is a practical fallback guide for {crop}. Prepare your field, verify seed quality, and match sowing with local weather.",
        "fertilizer_schedule": "Use compost or well-decomposed FYM before sowing. Apply nitrogen, phosphorus, and potassium in split doses based on soil test results.",
        "pest_watch": "Watch for early signs of sucking pests, fungal spots, and moisture-related diseases. Inspect the crop regularly, especially after rainfall.",
        "harvest_window": "Harvest when the crop reaches full maturity and grain or fruit quality is stable. Avoid harvesting during wet conditions.",
        "tips": "Keep irrigation balanced, remove weeds early, and prefer a soil test before adding extra fertilizer.",
    }


def show_crop_advisor(t, common_crops, settings):
    """
    Display the Crop Advisor page.
    
    Args:
        t: Translation function
        common_crops: List of common crops from config
        settings: AI provider settings dictionary
    """
    st.title(t("crop_advisor_title"))
    st.write(t("crop_advisor_description"))
    
    # Create form for crop advice
    with st.form("crop_advisor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            crop = st.selectbox(
                t("crop_advisor_crop_label"),
                options=common_crops
            )
            district = st.text_input(
                t("crop_advisor_district_label"),
                placeholder=t("crop_advisor_district_placeholder")
            )
        
        with col2:
            state = st.text_input(
                t("crop_advisor_state_label"),
                placeholder=t("crop_advisor_state_placeholder")
            )
            sowing_date = st.date_input(
                t("crop_advisor_date_label"),
                value=datetime.now()
            )
        
        submitted = st.form_submit_button(
            t("crop_advisor_submit"),
            use_container_width=True
        )
    
    if submitted:
        # Validate inputs
        if not district or not state:
            st.error(t("error_generic"))
        else:
            with st.spinner(t("loading")):
                try:
                    # Get current language from session state
                    lang = st.session_state.get("lang", "en")
                    
                    # Call backend function
                    result = _get_crop_advice(
                        crop=crop,
                        district=district,
                        state=state,
                        sowing_date=sowing_date.strftime("%Y-%m-%d"),
                        lang=lang,
                        settings=settings
                    )
                    
                    # Check for errors
                    if "error" in result:
                        error_message = result["error"]
                        if "Cannot connect to Ollama" in error_message or "selected AI provider" in error_message:
                            st.success(t("success"))
                            result = _fallback_crop_advice(crop)
                            
                            # Show date warning if present (from the earlier call)
                            if "date_warning" in result:
                                st.warning(f"⚠️ **Date Alert**: {result.get('date_warning')}", icon="⚠️")

                            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                                t("crop_advisor_seasonal_plan"),
                                t("crop_advisor_fertilizer"),
                                t("crop_advisor_pest_watch"),
                                t("crop_advisor_harvest"),
                                t("crop_advisor_tips")
                            ])

                            with tab1:
                                st.markdown(result.get("seasonal_plan", "No information available"))

                            with tab2:
                                st.markdown(result.get("fertilizer_schedule", "No information available"))

                            with tab3:
                                st.markdown(result.get("pest_watch", "No information available"))

                            with tab4:
                                st.markdown(result.get("harvest_window", "No information available"))

                            with tab5:
                                st.markdown(result.get("tips", "No information available"))
                        else:
                            st.error(error_message)
                    else:
                        # Display results in tabs
                        st.success(t("success"))
                        
                        # Show date warning if present
                        if result.get("date_warning"):
                            st.warning(f"⚠️ **Date Alert**: {result.get('date_warning')}", icon="⚠️")
                        
                        tab1, tab2, tab3, tab4, tab5 = st.tabs([
                            t("crop_advisor_seasonal_plan"),
                            t("crop_advisor_fertilizer"),
                            t("crop_advisor_pest_watch"),
                            t("crop_advisor_harvest"),
                            t("crop_advisor_tips")
                        ])
                        
                        with tab1:
                            st.markdown(result.get("seasonal_plan", "No information available"))
                        
                        with tab2:
                            st.markdown(result.get("fertilizer_schedule", "No information available"))
                        
                        with tab3:
                            st.markdown(result.get("pest_watch", "No information available"))
                        
                        with tab4:
                            st.markdown(result.get("harvest_window", "No information available"))
                        
                        with tab5:
                            st.markdown(result.get("tips", "No information available"))
                
                except Exception as e:
                    st.error(f"{t('error_generic')}: {str(e)}")