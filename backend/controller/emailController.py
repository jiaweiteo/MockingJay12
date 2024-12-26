import streamlit as st

def send_agenda_email(meeting_id, agenda_status):
    # As a button using HTML
    st.markdown(f"""
        <a href="mailto:example@email.com" style="text-decoration: none;">
            <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                Send {agenda_status} Email
            </button>
        </a>
    """, unsafe_allow_html=True)

def send_item_email(meeting_id, meeting_details):
    return "mailto:example@email.com"
