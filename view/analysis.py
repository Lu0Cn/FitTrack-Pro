import streamlit as st
import database as db
import utils_i18n as i18n
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_analysis(lang):
    st.header(i18n.get_text(lang, "analysis_title"))
    
    # --- Macro Breakdown ---
    st.subheader(i18n.get_text(lang, "macro_breakdown"))
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    food_logs = db.get_food_logs(today)
    
    if not food_logs.empty:
        macros = food_logs[['protein', 'carbs', 'fat']].sum()
        if macros.sum() > 0:
            fig = px.pie(
                values=macros.values, 
                names=macros.index, 
                title=i18n.get_text(lang, "today_macros"),
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#FFE66D'] # Protein-Red, Carbs-Teal, Fat-Yellow
            )
            st.plotly_chart(fig)
        else:
            st.info(i18n.get_text(lang, "log_food_msg"))
    else:
        st.info(i18n.get_text(lang, "log_food_msg"))

    # --- Correlation ---
    st.subheader(i18n.get_text(lang, "wellness_corr"))
    # Join Daily metrics
    conn = db.sqlite3.connect(db.DB_FILE)
    df = pd.read_sql("SELECT * FROM daily_metrics ORDER BY date DESC LIMIT 30", conn)
    conn.close()
    
    if not df.empty and len(df) > 2:
        fig = px.scatter(df, x='sleep_hours', y='mood_score', size='stress_level', 
                         title=i18n.get_text(lang, "sleep_vs_mood"),
                         trendline="ols")
        st.plotly_chart(fig)
    else:
        st.info(i18n.get_text(lang, "need_more_data"))

    # --- Activity Heatmap (Last 30 Days) ---
    st.subheader(i18n.get_text(lang, "activity_heatmap"))
    conn = db.sqlite3.connect(db.DB_FILE)
    # Get all exercise logs for last 60 days
    df_ex = pd.read_sql("SELECT date, calories_burned FROM exercise_logs ORDER BY date", conn)
    conn.close()
    
    if not df_ex.empty:
        # Aggregate by date
        df_ex['date'] = pd.to_datetime(df_ex['date'])
        daily_burn = df_ex.groupby('date')['calories_burned'].sum().reset_index()
        
        # Create calendar-style heatmap
        daily_burn['week'] = daily_burn['date'].dt.isocalendar().week
        daily_burn['day_num'] = daily_burn['date'].dt.dayofweek
        
        # Pivot for heatmap
        pivot_table = daily_burn.pivot(index='day_num', columns='week', values='calories_burned')
        
        # Reindex to ensure all 7 days are present (0=Mon to 6=Sun)
        pivot_table = pivot_table.reindex(range(7), fill_value=0)
        
        # Map day nums to names for y-axis
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        fig_map = px.imshow(pivot_table, 
                            labels=dict(x=i18n.get_text(lang, "heatmap_x"), y=i18n.get_text(lang, "heatmap_y"), color=i18n.get_text(lang, "heatmap_color")),
                            y=i18n.get_text(lang, "days_short"),
                            color_continuous_scale="Greens")
        fig_map.update_layout(height=400)
        st.plotly_chart(fig_map)
    else:
        st.info(i18n.get_text(lang, "no_ex_data"))
