import streamlit as st
import streamlit as st

from backend.controller.meetingController import *
from datetime import datetime
from streamlit_calendar import calendar


def formatDate(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%b %d, %Y")
    return formatted_date

# Streamlit app
st.title(":calendar: MockingJay")

"""
**This is a single-stop platform for managing HODM processes and progress**

### HOD Meeting (HODM)
Purpose:

1. Approve implementation of Workplans and major organisation-level initiatives & policies

2. Approve first cut concepts & implementation of minor organisation-level initiatives & policies

(Note: Use HODM if your item requires input from a majority of the HODs).

**Frequency: Twice monthly, 2.5hrs**

**Secretariat Email: test@gmail.com**
"""

st.subheader("Upcoming HODM Meetings")
# Fetch card data from the database
meetings = load_meeting_data()


# Convert meetings to events
events = [{"date": m["meetingDate"], "title": m["meetingTitle"]} for m in meetings]

selected_date = calendar(events)

# # Show details of the selected date
# if selected_date:
#     st.subheader(f"Meetings on {selected_date}")
#     for meeting in [m for m in meetings if m["meetingDate"] == selected_date]:
#         st.write(meeting["meetingTitle"])

# Render cards
for meeting in meetings:
    meeting_url = f"/meeting?id={meeting['id']}"  # Link to card details page
    formatted_date = formatDate(meeting['meetingDate'])
    st.markdown(
        f"""
        <a href="{meeting_url}" style="text-decoration: none;">
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">{meeting['meetingTitle']} HODM</h4>
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

