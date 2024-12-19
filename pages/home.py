import streamlit as st

from backend.controller.meetingController import *
from streamlit_calendar import calendar
from utils.dateUtils import *
from utils.constants import Role

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "businessHours": {
        "daysOfWeek": [1, 2, 3, 4, 5],
        "startTime": "09:00",
        "endTime": "18:00"
    }
}

custom_css="""
    .fc {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .fc-event-past {
        opacity: 0.8;
    }

    .fc-event-time {
        font-style: italic;
    }

    .fc-event-title {
        font-weight: 700;
    }
    
    .fc-toolbar-title {
        font-size: 2rem;
    }

    th.fc-day-sun, th.fc-day-sat, td.fc-day-sun, td.fc-day-sat {
        display: none !important;
    }
"""

@st.dialog("DM Details")
def handle_event_click(event):
    meeting = event["eventClick"]["event"]
    meeting_url = f"/meeting?id={meeting['id']}"  # Link to card details page
    date, start_time = datetime_string_to_date_and_time_object(meeting['start'])
    _, end_time = datetime_string_to_date_and_time_object(meeting['end'])
    st.markdown(
        f"""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">{meeting['title']} DM</h4>
                <p style="color: #666;">
                    Date: {format_date(date.strftime("%Y-%m-%d"))}<br>
                    Start Time: {start_time}<br>
                    End Time: {end_time}
                </p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(label="View More", url=meeting_url)

def render_meeting_card(meeting):
    meeting_url = f"/meeting?id={meeting['id']}"  # Link to card details page
    formatted_date = format_date(meeting['meetingDate'])
    st.markdown(
        f"""
        <a target="_self" href="{meeting_url}" style="text-decoration: none;">
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">{meeting['meetingTitle']} DM</h4>
                <h6 style="color: #666;">{meeting['description']}</h6>
                <p style="color: #666;">
                    Time: {formatted_date}, {meeting['startTime']} - {meeting['endTime']}
                    <br>
                    Location: {meeting['location']}
                </p>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

# Streamlit app
st.title(":calendar: MockingJay")

leftCol, rightCol = st.columns([3, 2])

with leftCol:
    with st.container(border=True):
        """
        ### Department Meeting (DM)
        Purpose:

        1. Lorem ipsum dolor sit amet, consectetur adipiscing elit.

        2.  Quisque eu mattis sapien. Cras dapibus ac leo nec ultricies.

        (Note: Cras egestas vulputate massa, sed tristique metus malesuada eget.).

        **Frequency: Cras id laoreet mi**

        **Email: test@gmail.com**
        """

    # Fetch card data from the database
    meetings = load_meeting_data()
    meetings = sorted(meetings, key=lambda x: x["meetingDate"])

    # Convert meetings to events
    events = [{
            "title": m["meetingTitle"], 
            "start": combine_date_and_time(m["meetingDate"], m["startTime"]), 
            "end": combine_date_and_time(m["meetingDate"], m["endTime"]),
            "display": "block",
            "id": m["id"]
            } 
            for m in meetings]

    with st.container(border=True):
        state = calendar(
            events=events,
            options=calendar_options,
            custom_css=custom_css
            )

        if state.get("callback") is not None and state.get("callback") == "eventClick":
            handle_event_click(state)

with rightCol:
    innerLeftCol, innerRightCol = st.columns([3, 1])
    with innerLeftCol:
        st.subheader("Meeting Forecast")
    with innerRightCol:
        if st.session_state.role == Role.SECRETARIAT.value:
            st.link_button(label="New Meeting", icon="➕", url="/meeting-form")
    # Render cards
    for meeting in meetings:
        render_meeting_card(meeting)
