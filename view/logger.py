import streamlit as st
import database as db
import ai_assistant as ai
import utils_i18n as i18n
from datetime import datetime
import pandas as pd

def render_logger(user_profile, lang):
    st.header(i18n.get_text(lang, "logger_title"))

    tab1, tab2, tab3, tab4 = st.tabs([
        i18n.get_text(lang, "tab_weight"), 
        i18n.get_text(lang, "tab_food"), 
        i18n.get_text(lang, "tab_ex"), 
        i18n.get_text(lang, "tab_metrics")
    ])

    # --- Weight Tab ---
    with tab1:
        st.subheader(i18n.get_text(lang, "log_weight_header"))
        with st.form("weight_form"):
            w_date = st.date_input(i18n.get_text(lang, "dob_lbl"), value=datetime.today()) # Reusing Date label
            weight = st.number_input(i18n.get_text(lang, "weight_lbl"), value=user_profile['current_weight'] if user_profile is not None else 70.0, step=0.1)
            
            c1, c2 = st.columns(2)
            body_fat = c1.number_input(i18n.get_text(lang, "body_fat_lbl"), min_value=0.0, max_value=100.0, step=0.1)
            muscle_rate = c2.number_input(i18n.get_text(lang, "muscle_rate_lbl"), min_value=0.0, max_value=100.0, step=0.1)
            
            note = st.text_area(i18n.get_text(lang, "note_lbl"))
            submitted = st.form_submit_button(i18n.get_text(lang, "save_weight_btn"))
            
            if submitted:
                db.add_weight_log(w_date.strftime("%Y-%m-%d"), weight, body_fat or None, muscle_rate or None, note)
                st.success(i18n.get_text(lang, "success_saved"))
                st.session_state['data_updated'] = True
                # Update user profile current weight too for convenience
                if user_profile is not None:
                    db.save_user_profile(user_profile['name'], user_profile['gender'], user_profile['birth_date'],
                                         user_profile['height'], weight, user_profile['target_weight'], 
                                         user_profile['activity_level'], user_profile['deepseek_api_key'])

        st.subheader(i18n.get_text(lang, "recent_history"))
        history = db.get_weight_history()
        if not history.empty:
            st.dataframe(history[['date', 'weight', 'body_fat', 'note']], hide_index=True)

    # --- Food Tab ---
    with tab2:
        st.subheader(i18n.get_text(lang, "log_food_header"))
        
        log_mode = st.radio("Mode", [i18n.get_text(lang, "mode_ai"), i18n.get_text(lang, "mode_manual")], horizontal=True)

        if i18n.get_text(lang, "mode_ai") in log_mode:
            st.info(i18n.get_text(lang, "ai_instruction"))
            food_text = st.text_area(i18n.get_text(lang, "what_did_eat"))
            
            if st.button(i18n.get_text(lang, "analyze_btn")):
                if user_profile is None or not user_profile['deepseek_api_key']:
                    st.error(i18n.get_text(lang, "setup_api_msg"))
                else:
                    with st.spinner(i18n.get_text(lang, "analyzing_msg")):
                        result = ai.parse_food_log(user_profile['deepseek_api_key'], food_text, lang=lang)
                        if "error" in result:
                            st.error(f"{i18n.get_text(lang, 'error_prefix')}{result['error']}")
                        else:
                            st.session_state['ai_food_result'] = result
            
            if 'ai_food_result' in st.session_state:
                st.write(i18n.get_text(lang, "ai_result_header"))
                results = st.session_state['ai_food_result']
                
                # Allow user to edit before saving
                with st.form("ai_review_form"):
                    final_items = []
                    for idx, item in enumerate(results):
                        c1, c2, c3 = st.columns([3, 1, 1])
                        name = c1.text_input(f"{i18n.get_text(lang, 'item_lbl')} {idx+1}", value=item['food_name'], key=f"name_{idx}")
                        cals = c2.number_input(i18n.get_text(lang, "kcal_lbl"), value=float(item['calories']), key=f"cal_{idx}")
                        f_date = st.date_input(i18n.get_text(lang, "date_lbl"), value=datetime.today(), key=f"date_{idx}")
                        final_items.append({"name": name, "cals": cals, "date": f_date, "p": item['protein'], "c": item['carbs'], "f": item['fat']})
                    
                    if st.form_submit_button(i18n.get_text(lang, "confirm_save_btn")):
                        for item in final_items:
                            db.add_food_log(item['date'].strftime("%Y-%m-%d"), "AI", item['name'], item['cals'], item['p'], item['c'], item['f'], "AI Log")
                        st.success(i18n.get_text(lang, "success_saved"))
                        st.session_state['data_updated'] = True
                        del st.session_state['ai_food_result']

        else: # Manual
            with st.form("manual_food_form"):
                f_date = st.date_input(i18n.get_text(lang, "date_lbl"), value=datetime.today())
                f_time = st.selectbox(i18n.get_text(lang, "meal_lbl"), i18n.get_text(lang, "meal_options"))
                name = st.text_input(i18n.get_text(lang, "food_name_lbl"))
                cals = st.number_input(i18n.get_text(lang, "calories_lbl"), min_value=0.0)
                
                c1, c2, c3 = st.columns(3)
                prot = c1.number_input(i18n.get_text(lang, "protein_lbl"), min_value=0.0)
                carbs = c2.number_input(i18n.get_text(lang, "carbs_lbl"), min_value=0.0)
                fat = c3.number_input(i18n.get_text(lang, "fat_lbl"), min_value=0.0)
                
                if st.form_submit_button(i18n.get_text(lang, "add_food_btn")):
                    db.add_food_log(f_date.strftime("%Y-%m-%d"), f_time, name, cals, prot, carbs, fat)
                    st.success(i18n.get_text(lang, "success_saved"))
                    st.session_state['data_updated'] = True

    # --- Exercise Tab ---
    with tab3:
        st.subheader(i18n.get_text(lang, "log_ex_header"))
        with st.form("exercise_form"):
            e_date = st.date_input(i18n.get_text(lang, "date_lbl"), value=datetime.today())
            e_type = st.text_input(i18n.get_text(lang, "ex_type_lbl"))
            duration = st.number_input(i18n.get_text(lang, "duration_lbl"), min_value=1)
            cals_burned = st.number_input(i18n.get_text(lang, "burned_lbl"), min_value=0)
            
            if st.form_submit_button(i18n.get_text(lang, "add_ex_btn")):
                db.add_exercise_log(e_date.strftime("%Y-%m-%d"), e_type, duration, cals_burned)
                st.success(i18n.get_text(lang, "success_saved"))
                st.session_state['data_updated'] = True

    # --- Daily Metrics Tab ---
    with tab4:
        st.subheader(i18n.get_text(lang, "daily_vitals_header"))
        with st.form("daily_form"):
            d_date = st.date_input(i18n.get_text(lang, "date_lbl"), value=datetime.today())
            sleep = st.slider(i18n.get_text(lang, "sleep_hours_lbl"), 0.0, 12.0, 7.0, 0.5)
            water = st.number_input(i18n.get_text(lang, "water_lbl"), value=2000, step=100)
            mood = st.slider(i18n.get_text(lang, "mood_score_lbl"), 1, 10, 7)
            stress = st.slider(i18n.get_text(lang, "stress_level_lbl"), 1, 10, 3)
            
            if st.form_submit_button(i18n.get_text(lang, "save_vitals_btn")):
                db.update_daily_metrics(d_date.strftime("%Y-%m-%d"), sleep, water, mood, stress)
                st.success(i18n.get_text(lang, "success_saved"))
                st.session_state['data_updated'] = True

