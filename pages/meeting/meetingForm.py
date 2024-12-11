import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id
from utils.dateUtils import date_string_to_date_obj, time_string_to_datetime_obj
from datetime import datetime

if st.query_params.get('id') is not None:
    meeting_id = st.query_params['id']
    meeting_details = fetch_meeting_by_id(meeting_id)
    st.title("Edit HODM Meeting")

else:
    meeting_details = None
    st.title("Create HODM Meeting")

title = date = description = startTime = endTime = totalDuration = location = None

if meeting_details is not None:
    title = meeting_details["meetingTitle"]
    date = meeting_details["meetingDate"]
    description = meeting_details["description"]
    startTime = meeting_details["startTime"]
    endTime = meeting_details["endTime"]
    totalDuration = meeting_details["totalDuration"]
    location = meeting_details["location"]

# Meeting Form
with st.form("meeting_form"):
    st.header("Meeting Details")
    
    # Input fields
    meeting_title = st.text_input("Meeting Title", placeholder="Enter the title of the meeting", value=title)
    meeting_date = st.date_input("Meeting Date", value=date_string_to_date_obj(date) if date is not None else None)
    description = st.text_area("Description", placeholder="Enter a brief description of the meeting", value=description)
    location = st.text_input("Location", placeholder="Enter the meeting location", value=location)

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Start Time", value=time_string_to_datetime_obj(startTime) if startTime is not None else None)

    with col2:
        end_time = st.time_input("End Time", value=time_string_to_datetime_obj(endTime) if endTime is not None else None)
        
    # Submit and Cancel buttons side by side
    empty_col, button_col1, button_col2 = st.columns([10,1,1])  # Equal width columns for buttons
    with button_col1:
        submit_button = st.form_submit_button("Submit")
    with button_col2:
        cancel_button = st.form_submit_button("Cancel")
    
    # Process form submission
    if submit_button:
        st.success("Meeting details submitted successfully!")
        st.write("Here is the submitted data:")
        st.write({
            "Meeting Title": meeting_title,
            "Meeting Date": meeting_date,
            "Description": description,
            "Start Time": start_time,
            "End Time": end_time,
            "Total Duration": (datetime.combine(meeting_date, end_time) - datetime.combine(meeting_date, start_time)).total_seconds()/60,
            "Location": location,
            "Created By": "Admin",
            "Created On": datetime.now(),
        })
    elif cancel_button:
        st.warning("Form submission canceled.")