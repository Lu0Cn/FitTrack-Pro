import streamlit as st
import database as db
import utils_i18n as i18n
from views import dashboard, logger, analysis, settings

# Page Config
st.set_page_config(
    page_title="FitTrack Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
db.init_db()

# Load User Profile
user_profile = db.get_user_profile()

# Initialize Session State for Language
if 'language' not in st.session_state:
    st.session_state['language'] = 'en' # Default

lang = st.session_state['language']

# Sidebar
with st.sidebar:
    st.title(i18n.get_text(lang, "app_title"))
    if user_profile is not None:
        st.write(f"{i18n.get_text(lang, 'welcome')}, **{user_profile['name']}**!")
    else:
        st.warning(i18n.get_text(lang, "setup_profile"))
    
    st.markdown("---")
    
    # Navigation
    nav_options = {
        "Dashboard": i18n.get_text(lang, "nav_dashboard"),
        "Logger": i18n.get_text(lang, "nav_logger"),
        "Analysis": i18n.get_text(lang, "nav_analysis"),
        "Settings": i18n.get_text(lang, "nav_settings")
    }
    
    # Reverse lookup for logic
    selection = st.radio("Navigation", list(nav_options.values()))
    
    # Find key from value
    nav = [k for k, v in nav_options.items() if v == selection][0]
    
    st.markdown("---")
    st.caption(i18n.get_text(lang, "footer_version"))

# Routing
if nav == "Dashboard":
    dashboard.render_dashboard(user_profile, lang)
elif nav == "Logger":
    logger.render_logger(user_profile, lang)
elif nav == "Analysis":
    analysis.render_analysis(lang)
elif nav == "Settings":
    settings.render_settings(lang)

