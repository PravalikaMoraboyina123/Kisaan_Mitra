"""
Scheme Finder page - Helps farmers discover relevant government schemes and subsidies.
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from modules.scheme_finder import find_schemes
import streamlit as st


def show_schemes(t, common_crops, indian_states, settings):
    """
    Display the Government Schemes page.
    
    Args:
        t: Translation function
        common_crops: List of common crops from config
        indian_states: List of Indian states from config
        settings: AI provider settings dictionary
    """
    st.title(t("schemes_title"))
    st.write(t("schemes_description"))
    
    # Create form for scheme finder
    with st.form("schemes_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            state = st.selectbox(
                t("schemes_state_label"),
                options=indian_states
            )
        
        with col2:
            crop = st.selectbox(
                t("schemes_crop_label"),
                options=common_crops
            )
        
        with col3:
            land_size = st.number_input(
                t("schemes_land_label"),
                min_value=0.1,
                max_value=1000.0,
                value=5.0,
                step=0.5
            )
        
        submitted = st.form_submit_button(
            t("schemes_submit"),
            use_container_width=True
        )
    
    if submitted:
        with st.spinner(t("loading")):
            try:
                # Get current language from session state
                lang = st.session_state.get("lang", "en")
                
                # Find relevant schemes
                schemes = find_schemes(
                    state=state,
                    crop=crop,
                    land_size=land_size,
                    lang=lang,
                    settings=settings
                )
                
                if not schemes:
                    st.warning("No schemes found for your profile.")
                else:
                    st.subheader(t("schemes_results_title"))
                    st.markdown(f"Found **{len(schemes)}** relevant schemes for you!")
                    
                    # Display each scheme as an expander
                    for i, scheme in enumerate(schemes, 1):
                        scheme_name = scheme.get("scheme_name", "Unknown Scheme")
                        
                        with st.expander(f"📋 {i}. {scheme_name}", expanded=False):
                            # Eligibility
                            st.markdown(f"**{t('schemes_eligibility')}:**")
                            st.write(scheme.get("eligibility", "Not specified"))
                            
                            # Benefit
                            st.markdown(f"**{t('schemes_benefit')}:**")
                            st.info(scheme.get("benefit", "Not specified"))
                            
                            # How to apply
                            st.markdown(f"**{t('schemes_how_to_apply')}:**")
                            st.write(scheme.get("how_to_apply", "Not specified"))
                            
                            # AI advice if available
                            if "ai_advice" in scheme:
                                st.markdown("**💡 AI Recommendation:**")
                                st.success(scheme["ai_advice"])
                    
                    # Summary statistics
                    with st.expander("📊 Scheme Summary"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Schemes", len(schemes))
                        
                        with col2:
                            central_schemes = sum(1 for s in schemes if "PM" in s.get("scheme_name", ""))
                            st.metric("Central Schemes", central_schemes)
                        
                        with col3:
                            state_schemes = len(schemes) - central_schemes
                            st.metric("State Schemes", state_schemes)
                    
                    # Important notes
                    st.markdown("### ⚠️ Important Notes")
                    st.markdown("""
                    - Always verify eligibility criteria on official government portals
                    - Keep all necessary documents ready before applying
                    - Application deadlines vary by scheme - check regularly
                    - Contact your local agriculture department for assistance
                    - Beware of fraudulent agents asking for money
                    """)
                    
                    # Quick links (placeholders)
                    st.markdown("### 🔗 Useful Links")
                    col_link1, col_link2 = st.columns(2)
                    
                    with col_link1:
                        st.markdown("[📱 PM-KISAN Portal](https://pmkisan.gov.in)")
                        st.markdown("[🛡️ PMFBY Portal](https://pmfby.gov.in)")
                    
                    with col_link2:
                        st.markdown("[💳 KCC Information](https://www.india.gov.in)")
                        st.markdown("[📋 State Agriculture Portal](https://agricoop.nic.in)")
                
            except Exception as e:
                st.error(f"{t('error_generic')}: {str(e)}")
    
    # Information section
    with st.expander("ℹ️ About Government Schemes"):
        st.markdown("""
        ### Common Documents Required:
        - Aadhaar Card
        - Land Records (7/12 extract, Khatauni, etc.)
        - Bank Account Details (IFSC, Account Number)
        - Mobile Number (linked with Aadhaar)
        - Passport-sized Photographs
        - Caste Certificate (if applicable)
        
        ### Application Tips:
        1. **Verify Eligibility**: Check all criteria before applying
        2. **Complete Documentation**: Gather all required documents
        3. **Online Registration**: Most schemes now have online portals
        4. **Track Status**: Use application reference numbers to track progress
        5. **Seek Help**: Visit Common Service Centres (CSCs) for assistance
        
        ### Benefits of Government Schemes:
        - **Financial Support**: Direct income support and subsidies
        - **Insurance Coverage**: Protection against crop failures
        - **Credit Access**: Easy loans at concessional rates
        - **Technology Adoption**: Support for modern farming techniques
        - **Market Linkages**: Better price realization for produce
        """)