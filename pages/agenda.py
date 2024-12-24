import streamlit as st
from typing import Dict, List
from backend.controller.meetingController import *
from backend.controller.itemController import *
from backend.controller.attendanceController import *
from pages.meeting import display_meeting
from utils.dateUtils import format_date
from utils.commonUtils import get_purpose_color_and_value

def style_df(col):
    styled_col = [""] * col.size
    if col.name == "purpose":
        styled_col = []
        purpose_colors ={
            "Tier 1 (For Approval)": "background-color: #a6ccf5",
            "Tier 1 (For Discussion)": "background-color: #a6ccf5",
            "Tier 2 (For Information)": "background-color: #f7d18b",
        }
        for _, value in col.items():
            styled_col.append(purpose_colors.get(value))
        
    return styled_col



def format_meeting_title(meeting: Dict) -> str:
    date_str = meeting.get('meetingDate', '')
    if date_str:
        try:
            date = format_date(date_str)
            return f"{meeting['meetingTitle']} ({date})"
        except ValueError:
            return meeting['meetingTitle']
    return meeting['meetingTitle']

def get_select_flag_value(flag: int) -> str:
    return ":blue[Select]" if flag == 1 else "Non-Select"

def displayAgenda(meeting_details):
    st.subheader("Meeting Items", divider=True)

    # Get agenda items for selected meeting
    agenda_items = get_sorted_items_by_id(meeting_details["id"])
    # Convert to DataFrame for editing
    if agenda_items:
        formatted_agenda = agenda_items.copy()  # Create a copy to avoid modifying original data
        for item in formatted_agenda:
            item["selectFlag"] = get_select_flag_value(item["selectFlag"])
            _, purpose_value = get_purpose_color_and_value(item["purpose"])
            item["purpose"] = purpose_value


        df = pd.DataFrame(
        formatted_agenda,
        columns=["id", "title", "description", "purpose", "selectFlag", "itemOwner", "additionalAttendees", "duration", "status"]
        )
        # Apply the styling
        df = df.style.apply(style_df)
        # Create an editable dataframe, secretariat can only edit duration and status of item
        edited_df = st.data_editor(
            df,
            column_config={
                "id": None,
                "title": st.column_config.TextColumn(
                    "Title",
                    required=True,
                    # disabled=True,
                ),
                "description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                    disabled=True,
                ),
                "selectFlag": st.column_config.SelectboxColumn(
                    "Select/Non-Select",
                    options=["Select", "Non-Select"],
                    required=True,
                    disabled=True,
                ),
                "purpose": st.column_config.TextColumn(
                    "Purpose",
                    width="medium",
                    disabled=True,
                ),
                "itemOwner": st.column_config.TextColumn(
                    "Item Owner",
                    required=True,
                    disabled=True,
                ),
                "additionalAttendees": st.column_config.TextColumn(
                    "Additional Attendees",
                    width="medium",
                    disabled=True,
                ),
                "duration": st.column_config.NumberColumn(
                    "Duration (minutes)",
                    min_value=0,
                    max_value=30,
                    required=True
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Approved", "Waitlisted", "Rejected"],
                    required=True,
                    width="medium",
                    help="Select the status of the agenda item",
                ),
            },
            num_rows="dynamic",
            use_container_width=True,
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