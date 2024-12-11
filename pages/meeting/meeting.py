import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, fetch_upcoming_meeting, delete_meeting
from datetime import datetime
from utils.dateUtils import *

meeting_id = None
delete_button = None
st.session_state.delete_modal = False

if st.query_params.get('id') is not None:
    meeting_id = st.query_params['id']
    meeting_details = fetch_meeting_by_id(meeting_id)
else:
    meeting_details = fetch_upcoming_meeting()
    meeting_id = meeting_details['id']

def confirm_delete(meeting_id):
    delete_meeting(meeting_id)
    st.rerun()

@st.dialog("Delete Meeting")
def handle_delete_meeting(title):
    home_url = "/"  # 
    st.markdown(
        f"""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">Are you sure you want to delete {title} HODM meeting?</h4>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Delete"):
        confirm_delete(meeting_id)

if meeting_details is None:
    st.title("No Meeting found. Invalid Meeting ID: " + meeting_id)
else:
    # Convert UNIX timestamp to human-readable format
    created_on_date = datetime.fromtimestamp(meeting_details["createdOn"]).strftime("%Y-%m-%d %H:%M:%S")

    # Page title
    st.title(meeting_details["meetingTitle"] + " HODM Meeting")
    st.write(meeting_details["description"])

    # Display meeting information
    with st.container():
        
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        # Left column content
        with col1:
            st.subheader("Details", divider="green")
            st.write(f"**Date:** {format_date(meeting_details['meetingDate'])}")
            st.write(f"**Time:** {meeting_details['startTime']} - {meeting_details['endTime']}")
            st.write(f"**Location:** {meeting_details['location']}")
            st.write(f"**Created By:** {meeting_details['createdBy']} (Created on {created_on_date})")
            st.markdown('</div>', unsafe_allow_html=True)

            col3, col4 = st.columns([1,3])
            with col3:
                st.link_button(label="Edit Meeting", url=f"/meeting-form?id={meeting_details['id']}", icon="📝")
            with col4:
                if st.button("Delete Meeting"):
                    st.session_state.delete_modal = True

        # Right column content
        with col2:
            st.subheader("Demand", divider=True)
            st.write(f"**Duration:** {meeting_details['totalDuration']} minutes")
            st.write(f"**Time Taken:** {meeting_details['minutesTaken']}")
            st.write(f"**Time Left:** {meeting_details['minutesLeft']}")
            st.progress(meeting_details["minutesTaken"] / meeting_details['totalDuration'])
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.subheader("Items Registered", divider="orange")

    if st.session_state.delete_modal:
        handle_delete_meeting(meeting_details["meetingTitle"])

print(st.session_state.delete_modal)