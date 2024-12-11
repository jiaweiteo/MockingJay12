import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, fetch_upcoming_meeting

def render_meeting():
    st.title("HODM Meeting Details")

    if st.query_params.get('id') is not None:
        meeting_id = st.query_params['id']
        card = fetch_meeting_by_id(meeting_id)
    else:
        card = fetch_upcoming_meeting()

    if card:
        st.subheader(card["meetingTitle"])
        st.write(f"Date: {card['meetingDate']}")
        # Add more fields as necessary
    else:
        st.write("Card not found!")

render_meeting()

