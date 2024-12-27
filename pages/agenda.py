import streamlit as st
from typing import Dict, List
from backend.controller.meetingController import *
from backend.controller.itemController import *
from backend.controller.attendanceController import *
from pages.meeting import display_meeting
from utils.dateUtils import format_date
from utils.commonUtils import get_purpose_color_and_value, format_meeting_title
from utils.constants import Purpose_Lookup, Meeting_Status
from backend.controller.emailController import send_agenda_email, send_item_email

def get_item_column_config(agenda_size : int):
    return {
        "id": None,
        "itemOrder": st.column_config.SelectboxColumn(
            "Order",
            options= [i for i in range(0, agenda_size+1)],
            required=True,
            help="Arrange the order of presentation, 0 indicates that item will not be presented.",
        ),
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
            required=True,
            help="Max duration = 30mins",
        ),
        "status": st.column_config.SelectboxColumn(
            "Status",
            options=["Pending", "Approved", "Waitlisted", "Rejected", "Registered"],
            required=True,
            width="medium",
            help="Select the status of the agenda item",
        ),
        "email": st.column_config.LinkColumn(
            "Send Email", 
            display_text="Email",
            disabled=True,
        ),
    }

def style_df(col):
    styled_col = [""] * col.size
    if col.name == "purpose":
        styled_col = []
        purpose_colors ={
            Purpose_Lookup.APPROVAL.value: "background-color: #a6ccf5",
            Purpose_Lookup.DISCUSSION.value: "background-color: #a6ccf5",
            Purpose_Lookup.INFO.value: "background-color: #f7d18b",
        }
        for _, value in col.items():
            styled_col.append(purpose_colors.get(value))
        
    return styled_col

def get_select_flag_value(flag: int) -> str:
    return ":blue[Select]" if flag == 1 else "Non-Select"

def displayAgenda(meeting_details):
    st.subheader("Meeting Agenda Items", divider=True)
    agenda_status = st.selectbox(    
        label="Agenda Status",
        options=[e.value for e in Meeting_Status],
        index = list(Meeting_Status).index(Meeting_Status(meeting_details["status"])),
        # value=meeting_details['status']
    )
    edit_status_col, create_email_col = st.columns([2,10])
    with edit_status_col:
        st.button(
            "Update Agenda Status",
            disabled= agenda_status == meeting_details["status"],
            # Update data in database
            on_click=update_meeting_status,
            args=(meeting_details["id"], agenda_status),
            key='update_agenda_status'
            )
    with create_email_col:
        if agenda_status != "Curation":
            send_agenda_email(meeting_details["id"], agenda_status)

    st.subheader("Tier 1 Items")
    # Get agenda items for selected meeting
    tier_1_items = get_items_by_id_and_tier(meeting_details["id"], 1)
    # Convert to DataFrame for editing
    if tier_1_items:
        tier_1_agenda = tier_1_items.copy()  # Create a copy to avoid modifying original data
        for item in tier_1_agenda:
            item["selectFlag"] = get_select_flag_value(item["selectFlag"])
            _, purpose_value = get_purpose_color_and_value(item["purpose"])
            item["purpose"] = purpose_value
            item["email"] = send_item_email(meeting_details["id"], meeting_details)


        tier1_df = pd.DataFrame(
        tier_1_agenda,
        columns=["itemOrder", "id", "title", "description", "purpose", "selectFlag", "itemOwner", "additionalAttendees", "duration", "status", "email"]
        )
        # Apply the styling
        tier1_df = tier1_df.style.apply(style_df)
        # Create an editable dataframe, secretariat can only edit duration and status of item
        tier1_edited_df = st.data_editor(
            tier1_df,
            column_config=get_item_column_config(len(tier_1_agenda)),
            num_rows="fixed",
            use_container_width=True,
            key="tier1_agenda_editor"
        )
        
        tier1_has_uncommitted_changes = any(len(v) for v in st.session_state.tier1_agenda_editor.values())
        st.button(
            "Update Tier 1 Items",
            disabled=not tier1_has_uncommitted_changes,
            # Update data in database
            on_click=update_agenda_table_data,
            args=(tier1_df, st.session_state.tier1_agenda_editor),
            key='tier1_agenda_commit'
            )
    else:
        st.info("No agenda items found for this meeting. Add new items using the data editor.")

    st.subheader("Tier 2 Items")
    tier_2_items = get_items_by_id_and_tier(meeting_details["id"], 2)
    # Convert to DataFrame for editing
    if tier_2_items:
        tier_2_agenda = tier_2_items.copy()  # Create a copy to avoid modifying original data
        for item in tier_2_agenda:
            item["selectFlag"] = get_select_flag_value(item["selectFlag"])
            _, purpose_value = get_purpose_color_and_value(item["purpose"])
            item["purpose"] = purpose_value
            item["email"] = send_item_email(meeting_details["id"], meeting_details)


        df = pd.DataFrame(
        tier_2_agenda,
        columns=["id", "title", "description", "purpose", "selectFlag", "itemOwner", "additionalAttendees", "status", "email"]
        )
        # Apply the styling
        tier2_df = df.style.apply(style_df)
        # Create an editable dataframe, secretariat can only edit duration and status of item
        tier2_edited_df = st.data_editor(
            tier2_df,
            column_config=get_item_column_config(len(tier_2_agenda)),
            num_rows="fixed",
            use_container_width=True,
            key="tier2_agenda_editor"
        )
        
        tier2_has_uncommitted_changes = any(len(v) for v in st.session_state.tier2_agenda_editor.values())
        st.button(
            "Update Tier 2 Items",
            disabled=not tier2_has_uncommitted_changes,
            # Update data in database
            on_click=update_status_table_data,
            args=(tier2_df, st.session_state.tier2_agenda_editor),
            key='tier2_agenda_commit'
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
