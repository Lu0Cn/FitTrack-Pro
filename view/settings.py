import streamlit as st
import database as db
import utils_i18n as i18n
from datetime import datetime

def render_settings(lang):
    st.header(i18n.get_text(lang, "settings_title"))

    # Language Switcher
    st.subheader(i18n.get_text(lang, "language_lbl"))
    current_lang_idx = 0 if lang == 'en' else 1
    new_lang = st.selectbox(i18n.get_text(lang, "select_lang"), ["English", "中文 (Chinese)"], index=current_lang_idx)
    
    if new_lang == "English" and lang != 'en':
        st.session_state['language'] = 'en'
        st.rerun()
    elif new_lang == "中文 (Chinese)" and lang != 'zh':
        st.session_state['language'] = 'zh'
        st.rerun()

    st.markdown("---")

    # Load existing profile
    profile = db.get_user_profile()
    
    # Defaults
    name_default = profile['name'] if profile is not None else "User"
    gender_default = profile['gender'] if profile is not None else "Male"
    dob_default = datetime.strptime(profile['birth_date'], "%Y-%m-%d") if profile is not None and profile['birth_date'] else datetime(1990, 1, 1)
    height_default = float(profile['height']) if profile is not None else 170.0
    weight_default = float(profile['current_weight']) if profile is not None else 70.0
    target_default = float(profile['target_weight']) if profile is not None else 65.0
    activity_default = profile['activity_level'] if profile is not None else "Sedentary (office job)"
    api_key_default = profile['deepseek_api_key'] if profile is not None else ""

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(i18n.get_text(lang, "name_lbl"), value=name_default)
            gender = st.selectbox(i18n.get_text(lang, "gender_lbl"), ["Male", "Female"], index=0 if gender_default=="Male" else 1)
            dob = st.date_input(i18n.get_text(lang, "dob_lbl"), value=dob_default, min_value=datetime(1900, 1, 1), max_value=datetime(2025, 12, 31))
        with col2:
            height = st.number_input(i18n.get_text(lang, "height_lbl"), value=height_default)
            current_weight = st.number_input(i18n.get_text(lang, "weight_lbl"), value=weight_default)
            target_weight = st.number_input(i18n.get_text(lang, "target_lbl"), value=target_default)
        
        activity_options = [
            "Sedentary (office job)",
            "Lightly active (1-3 days/week)",
            "Moderately active (3-5 days/week)",
            "Very active (6-7 days/week)",
            "Super active (physical job)"
        ]
        activity_level = st.selectbox(i18n.get_text(lang, "activity_lbl"), activity_options, 
            index=["Sedentary", "Lightly", "Moderately", "Very", "Super"].index(activity_default.split()[0]),
            format_func=lambda x: i18n.get_text(lang, "act_" + x.split()[0].lower()))

        st.subheader(i18n.get_text(lang, "ai_integration_header"))
        deepseek_api_key = st.text_input(i18n.get_text(lang, "api_key_lbl"), value=api_key_default, type="password")
        st.caption(i18n.get_text(lang, "api_caption"))

        submitted = st.form_submit_button(i18n.get_text(lang, "save_profile_btn"))
        if submitted:
            db.save_user_profile(
                name, gender, dob.strftime("%Y-%m-%d"), height, 
                current_weight, target_weight, activity_level, deepseek_api_key
            )
            st.success(i18n.get_text(lang, "saved_msg"))
            st.balloons()
