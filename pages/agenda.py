import streamlit as st
from typing import Dict, List
from backend.controller.meetingController import *
from backend.controller.itemController import *
from backend.controller.attendanceController import *
from pages.meeting import display_meeting
from utils.dateUtils import format_date

def format_meeting_title(meeting: Dict) -> str:
    date_str = meeting.get('meetingDate', '')
    if date_str:
        try:
            date = format_date(date_str)
            return f"{meeting['meetingTitle']} ({date})"
        except ValueError:
            return meeting['meetingTitle']
    return meeting['meetingTitle']

def displayAgenda(meeting_details):
    st.subheader("Items", divider=True)

    # Get agenda items for selected meeting
    agenda_items = get_sorted_items_by_id(meeting_details["id"])
    print(agenda_items)
    df = pd.DataFrame(
    agenda_items,
    )

    # Convert to DataFrame for editing
    if agenda_items:
        # Create an editable dataframe
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID",
                    disabled=True,
                    required=True
                ),
                "meetingId": st.column_config.NumberColumn(
                    "Meeting ID",
                    disabled=True,
                    required=True
                ),
                "itemTitle": st.column_config.TextColumn(
                    "Title",
                    required=True
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Approved", "Waitlisted", "Rejected"],
                    required=True
                ),
                "description": st.column_config.TextColumn(
                    "Description",
                    width="large"
                ),
                "duration": st.column_config.NumberColumn(
                    "Duration (minutes)",
                    min_value=0,
                    max_value=480,
                    required=True
                ),
                "purpose": st.column_config.TextColumn(
                    "Purpose",
                    width="medium"
                ),
                "owner": st.column_config.TextColumn(
                    "Owner",
                    required=True
                ),
                "additionalAttendees": st.column_config.TextColumn(
                    "Additional Attendees",
                    width="medium"
                )
            },
            hide_index=True,
            num_rows="dynamic",
            key="agenda_editor"
        )
        
        has_uncommitted_changes = any(len(v) for v in st.session_state.agenda_editor.values())
        st.button(
            "Update Agenda",
            disabled=not has_uncommitted_changes,
            # Update data in database
            on_click=update_agenda_table_data,
            args=(df, st.session_state.agenda_editor),
            key='agenda_commit'
            )
    else:
        st.info("No agenda items found for this meeting. Add new items using the data editor.")

st.title("Meeting Agenda")

# Get available meetings
meetings = load_meeting_data()
meetings = sorted(meetings, key=lambda x: x["meetingDate"])
if not meetings:
    st.warning("No meetings found in the database.")

# Create a dictionary for easy lookup of meeting IDs
meeting_dict = {format_meeting_title(meeting): meeting["id"] for meeting in meetings}

# Meeting selector using formatted titles
selected_meeting_title = st.selectbox(
    "Select Meeting",
    options=list(meeting_dict.keys()),
)

# Get the selected meeting ID
selected_meeting_id = meeting_dict[selected_meeting_title]
meeting_details = fetch_meeting_by_id(selected_meeting_id)

display_meeting(meeting_id=selected_meeting_id, meeting_details=meeting_details)
displayAgenda(meeting_details)