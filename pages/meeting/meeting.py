import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, fetch_upcoming_meeting
from datetime import datetime
from utils.dateUtils import *

if st.query_params.get('id') is not None:
    meeting_id = st.query_params['id']
    meeting_details = fetch_meeting_by_id(meeting_id)
else:
    meeting_details = fetch_upcoming_meeting()

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
            st.link_button(label="Delete Meeting", url=f"/meeting-form?id={meeting_details['id']}", icon="❌")

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