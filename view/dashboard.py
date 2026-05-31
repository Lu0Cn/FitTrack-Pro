import streamlit as st
import database as db
import utils
import utils_i18n as i18n
import ai_assistant as ai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_dashboard(user_profile, lang):
    st.header(i18n.get_text(lang, "dash_title"))
    
    today_str = datetime.today().strftime("%Y-%m-%d")
    
    # Fetch Data
    food_today = db.get_food_logs(today_str)
    ex_today = db.get_exercise_logs(today_str)
    daily_metrics = db.get_daily_metrics(today_str)
    
    c_in = food_today['calories'].sum() if not food_today.empty else 0
    c_out = ex_today['calories_burned'].sum() if not ex_today.empty else 0
    
    # Calculate BMR & TDEE (Base Burn)
    if user_profile is not None:
        age = utils.calculate_age(user_profile['birth_date'])
        bmr = utils.calculate_bmr(user_profile['current_weight'], user_profile['height'], age, user_profile['gender'])
        tdee = utils.calculate_tdee(bmr, user_profile['activity_level'])
        total_burn = tdee + c_out
        net_cal = c_in - total_burn
    else:
        bmr, tdee, total_burn, net_cal = 0, 0, 0, 0

    # --- 1. AI Coach Section (Top, Horizontal) ---
    st.subheader(i18n.get_text(lang, "ai_coach_title"))
    
    # Check if we should auto-generate advice
    advice_key = f"advice_{today_str}"
    
    # Logic: 
    # 1. Data Updated Flag is SET -> Generate New
    # 2. No Advice Cached BUT Data Exists (First Load) -> Generate New
    # 3. Advice Cached -> Show Cached
    
    has_data = (not food_today.empty or not ex_today.empty)
    need_generation = False
    
    if user_profile is not None and user_profile['deepseek_api_key']:
        if st.session_state.get('data_updated', False):
            need_generation = True
        elif advice_key not in st.session_state and has_data:
            need_generation = True
            
        if need_generation:
            with st.spinner(i18n.get_text(lang, "analyzing_msg")):
                # Determine trend
                trend = "Stable" 
                history = db.get_weight_history(7)
                if len(history) >= 2:
                    delta = history.iloc[0]['weight'] - history.iloc[-1]['weight']
                    if delta > 0.5: trend = "Gaining"
                    elif delta < -0.5: trend = "Losing"
                
                advice = ai.generate_daily_advice(
                    user_profile['deepseek_api_key'],
                    user_profile.to_dict(),
                    {"eaten": c_in, "burned": total_burn, "sleep": daily_metrics['sleep_hours'] if daily_metrics is not None else "?"},
                    trend,
                    lang=lang
                )
                st.session_state[advice_key] = advice
                st.session_state['data_updated'] = False
        
        if advice_key in st.session_state:
            st.info(st.session_state[advice_key], icon="🤖")
        elif not has_data:
            st.info(i18n.get_text(lang, "advice_prompt"), icon="ℹ️")
    else:
         st.error(i18n.get_text(lang, "setup_api_msg"))

    st.markdown("---")

    # --- 2. KPI Row ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(i18n.get_text(lang, "cal_in"), f"{int(c_in)} kcal")
    col2.metric(i18n.get_text(lang, "ex_burn"), f"{int(c_out)} kcal")
    col3.metric(i18n.get_text(lang, "total_burn"), f"{int(total_burn)} kcal", help="TDEE + Exercise")
    col4.metric(i18n.get_text(lang, "net_bal"), f"{int(net_cal)} kcal", delta_color="inverse")
    
    st.markdown("---")

    # --- 3. Visualizations Row 1 (Weight & BMI) ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader(i18n.get_text(lang, "weight_trend"))
        history = db.get_weight_history(30)
        if not history.empty:
            history['date'] = pd.to_datetime(history['date'])
            fig = px.line(history, x='date', y='weight', markers=True)
            if user_profile is not None:
                fig.add_hline(y=user_profile['target_weight'], line_dash="dash", annotation_text=i18n.get_text(lang, 'target_label'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(i18n.get_text(lang, "no_weight_msg"))

    with c2:
        st.subheader(i18n.get_text(lang, "bmi_title"))
        if user_profile is not None:
            # BMI Calc
            height_m = user_profile['height'] / 100
            weight = user_profile['current_weight']
            bmi = weight / (height_m ** 2)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = bmi,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "BMI"},
                gauge = {
                    'axis': {'range': [10, 40]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 18.5], 'color': "lightblue"}, # Underweight
                        {'range': [18.5, 24.9], 'color': "lightgreen"}, # Normal
                        {'range': [24.9, 29.9], 'color': "orange"}, # Overweight
                        {'range': [29.9, 50], 'color': "red"} # Obese
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': bmi
                    }
                }
            ))
            fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.write(i18n.get_text(lang, "setup_bmi_msg"))

    # --- 4. Visualizations Row 2 (Weekly & Radar) ---
    c3, c4 = st.columns([1, 1])
    
    with c3:
        st.subheader(i18n.get_text(lang, "weekly_cal_bal")) # TODO: i18n
        dates = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        weekly_in = []
        weekly_limit = []
        
        for d in dates:
            f = db.get_food_logs(d)
            weekly_in.append(f['calories'].sum() if not f.empty else 0)
            weekly_limit.append(tdee)

        fig_bar = go.Figure(data=[
            go.Bar(name=i18n.get_text(lang, "cal_in"), x=dates, y=weekly_in),
            go.Scatter(name=i18n.get_text(lang, "burn_target"), x=dates, y=weekly_limit, mode='lines+markers', line=dict(color='red', dash='dash'))
        ])
        fig_bar.update_layout(barmode='group', height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c4:
        st.subheader(i18n.get_text(lang, "wellness_radar"))
        # Radar Chart Data
        # Dimensions: Sleep (Norm/8), Mood (Av/10), Stress (10-Av)/10, ActivityFreq (Days/7)
        
        if daily_metrics is not None:
             sleep_score = min(daily_metrics['sleep_hours'], 8) / 8 * 10 
             mood_score = daily_metrics['mood_score']
             stress_score = 10 - daily_metrics['stress_level'] # Invert so higher is better
        else:
             sleep_score, mood_score, stress_score = 0, 0, 0
             
        # Simple activity check for "Consistency" (log count in last 7 days)
        # Using placeholder 5 for now as getting 7 days history here is expensive without query
        # Let's just use "Today's Activity" - burned / 500 * 10?
        activity_score = min(total_burn / 2500 * 10, 10) # 2500 as rough target
        
        categories = [i18n.get_text(lang, "radar_sleep"), i18n.get_text(lang, "radar_mood"), i18n.get_text(lang, "radar_stress"), i18n.get_text(lang, "radar_activity")]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[sleep_score, mood_score, stress_score, activity_score],
            theta=categories,
            fill='toself',
            name=i18n.get_text(lang, "wellness_score")
        ))
        fig_radar.update_layout(
          polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
          ),
          showlegend=False,
          height=350
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- Recent Logs ---
    st.subheader(i18n.get_text(lang, "today_logs"))
    if not food_today.empty:
        st.dataframe(food_today[['time', 'food_name', 'calories', 'protein', 'carbs', 'fat']], hide_index=True)

