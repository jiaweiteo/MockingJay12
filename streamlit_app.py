import streamlit as st
from utils.constants import Role
# from collections import defaultdict
# from pathlib import Path
# from streamlit.source_util import get_pages

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Meeting Management",
    page_icon=":calendar:",
    layout="wide"
)

st.logo('static/logo.jpg')

css = '''
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Source+Code+Pro:wght@300;400;600&display=swap');

html * {
    font-family: 'Poppins', sans-serif !important;
}
'''

st.markdown(
        f"""
        <style>
        {css}    
        </style>
        """,
        unsafe_allow_html=True,
    )

# Retrieve role from keycloak headers through OPA policy
if "role" not in st.session_state:
    st.session_state.role = Role.SECRETARIAT.value

role = st.session_state.role

home_page = st.Page('pages/home.py', title='Overview', icon='🏠')

meeting_page = st.Page('pages/meeting/meeting.py', title='Meeting', icon='💼')
meeting_form_page = st.Page('pages/meeting/meetingForm.py', title='New Meeting', icon='➕', url_path="/meeting-form")

agenda_page = st.Page('pages/preMeeting/agenda.py', title='Agenda', icon='📜')
item_form_page = st.Page('pages/preMeeting/itemForm.py', title='New Item', icon='📖', url_path="/item-form")
minutes_page = st.Page('pages/minutes.py', title='Note-Taking', icon='📝')

dependencies_page = st.Page('pages/dependencies.py', title='Dependencies')
database_page = st.Page('pages/database.py', title='Database')
settings_page = st.Page('pages/settings.py', title='Settings', icon='⚙️')

attendance_page = st.Page('pages/attendance.py', title='Update Attendance', icon='🈁')

general_pages = [home_page, meeting_page, item_form_page, settings_page]
assistant_pages = [home_page, meeting_page, attendance_page, item_form_page, settings_page]
secretariat_pages = {
  'Home': [
      home_page,
      meeting_page,
      meeting_form_page,
    ],
    'Pre-Meeting': [
        item_form_page,
        agenda_page,
    ],
    'Meeting': [
        minutes_page,
    ],
    'Admin': [
        dependencies_page,
        database_page,
        settings_page
    ]
}

if (role == Role.SECRETARIAT.value):
    nav = st.navigation(secretariat_pages)
elif (role == Role.PERSONAL_ASSISTANT.value):
    nav = st.navigation(assistant_pages)
else:
    nav = st.navigation(general_pages)
nav.run()