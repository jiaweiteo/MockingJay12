import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, create_meeting, update_meeting
from utils.dateUtils import date_string_to_date_obj, time_string_to_datetime_obj
from datetime import datetime

# Callback function to update end time
def update_end_time():
    global start_time, end_time
    if start_time:
        start_datetime = datetime.datetime.combine(datetime.date.today(), start_time)
        end_datetime = start_datetime + datetime.timedelta(hours=2)
        end_time = end_datetime.time()

meeting_id = None
if st.query_params.get('id') is not None:
    meeting_id = st.query_params['id']
    meeting_details = fetch_meeting_by_id(meeting_id)
    st.title("Edit HODM Meeting")

else:
    meeting_details = None
    st.title("Create HODM Meeting")

start_time = end_time = None
title = date = description = startTime = endTime = totalDuration = location = None
create_button = update_button = cancel_button = None

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
        
    empty_col, button_col1 = st.columns([15,1])  # Equal width columns for buttons
    with button_col1:
        if meeting_id is not None:
            update_button = st.form_submit_button("Update Meeting")
        else:
            create_button = st.form_submit_button("Create Meeting")    

    # Process form submission
    if create_button:
        total_duration = (datetime.combine(meeting_date, end_time) - datetime.combine(meeting_date, start_time)).total_seconds()/60
        meeting_data = {
            "meetingTitle": meeting_title,
            "meetingDate": meeting_date,
            "description": description,
            "startTime": str(start_time),
            "endTime": str(end_time),
            "totalDuration": total_duration,
            "minutesLeft": total_duration,
            "minutesTaken": 0,
            "location": location,
            "createdBy": "Admin",
            "createdOn": datetime.now().timestamp()
        }
        create_meeting(meeting_data)
        st.success("Meeting details submitted successfully!")
        st.write("Here is the submitted data:")
        st.write(meeting_data)
    elif update_button:
        total_duration = (datetime.combine(meeting_date, end_time) - datetime.combine(meeting_date, start_time)).total_seconds()/60
        meeting_data = {
            "meetingTitle": meeting_title,
            "meetingDate": meeting_date,
            "description": description,
            "startTime": str(start_time),
            "endTime": str(end_time),
            "totalDuration": total_duration,
            "minutesLeft": total_duration,
            "minutesTaken": 0,
            "location": location,
        }
        update_meeting(meeting_id, meeting_data)
        st.success("Meeting details updated successfully!")
        st.write("Here is the submitted data:")
        st.write(meeting_data)
