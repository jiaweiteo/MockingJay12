import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, create_meeting, update_meeting
from datetime import datetime, time, timedelta
from utils.dateUtils import date_string_to_date_obj, time_string_to_datetime_obj
from streamlit_extras.switch_page_button import switch_page 
from utils.constants import Meeting_Status

# Callback function to update end time
def update_end_time(current_time):
    current_date_time = datetime.combine(datetime.now(), current_time)
    new_end_time = current_date_time + timedelta(hours=2.5)
    return new_end_time.time()

@st.fragment
def display_meeting_form():
    global meeting_id
    global meeting_details
    global title
    start_time = end_time = None
    meeting_title_temp = date = description = totalDuration = location = None
    create_button = update_button = cancel_button = None

    startTime = time(15, 0)
    endTime = update_end_time(startTime)

    if st.query_params.get('id') is not None or meeting_id is not None:
        if meeting_id is not None:
            meeting_details = fetch_meeting_by_id(meeting_id)
        else:
            meeting_id = st.query_params['id']
            meeting_details = fetch_meeting_by_id(meeting_id)
        title = ("Edit DM Meeting")

    else:
        meeting_details = None
        title = ("Create DM Meeting")        

    if meeting_details is not None:
        meeting_title_temp = meeting_details["meetingTitle"]
        date = meeting_details["meetingDate"]
        description = meeting_details["description"]
        startTime = time_string_to_datetime_obj(meeting_details["startTime"])
        endTime = time_string_to_datetime_obj(meeting_details["endTime"])
        totalDuration = meeting_details["totalDuration"]
        location = meeting_details["location"]

    # Meeting Title
    st.title(title)

    button_html = f"""
    <a target="_self" href="/meeting?id={meeting_id}" style="text-decoration: none;">
        <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                Go to Meeting
        </button>
    </a>
    """
    if (meeting_id is not None):
        st.markdown(button_html, unsafe_allow_html=True)

    st.divider()

    # Meeting Form
    with st.form("meeting_form"):
        st.header("Meeting Details")
        
        # Input fields
        meeting_title = st.text_input("Meeting Title", placeholder="Enter the title of the meeting", value=meeting_title_temp)
        meeting_date = st.date_input("Meeting Date", value=date_string_to_date_obj(date) if date is not None else "today", min_value="today")
        description = st.text_area("Description", placeholder="Enter a brief description of the meeting", value=description)
        location = st.text_input("Location", placeholder="Enter the meeting location", value=location)

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", value=startTime)
        with col2:
            end_time = st.time_input("End Time", value=endTime)
            
        _, button_col1 = st.columns([15, 1])  # Equal width columns for buttons
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
                "startTime": str(start_time)[:-3],
                "endTime": str(end_time)[:-3],
                "totalDuration": total_duration,
                "minutesLeft": total_duration,
                "minutesTaken": 0,
                "location": location,
                "createdBy": "Admin",
                "createdOn": datetime.now().timestamp(),
                "status": Meeting_Status.CURATION.value,
            }
            meeting_id = create_meeting(meeting_data)
            st.success("Meeting created successfully!")
            st.rerun(scope="fragment")

        elif update_button:
            total_duration = (datetime.combine(meeting_date, end_time) - datetime.combine(meeting_date, start_time)).total_seconds()/60
            meeting_data = {
                "meetingTitle": meeting_title,
                "meetingDate": meeting_date,
                "description": description,
                "startTime": str(start_time)[:-3],
                "endTime": str(end_time)[:-3],
                "totalDuration": total_duration,
                "minutesLeft": total_duration,
                "minutesTaken": 0,
                "location": location,
            }
            meeting_id=update_meeting(meeting_id, meeting_data)
            st.success("Meeting details updated successfully!")
            st.rerun(scope="fragment")

meeting_id = meeting_details = title = None
display_meeting_form()
