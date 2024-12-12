import streamlit as st
from urllib.parse import parse_qs
from backend.controller.meetingController import fetch_meeting_by_id, load_meeting_data
from backend.controller.itemController import create_item, get_item_by_id, update_item
from utils.dateUtils import format_date
import pandas as pd
from utils.constants import Item_Status
from datetime import datetime
import numpy as np


purposeLookup = ["Tier 1 (For Approval)", "Tier 1 (For Discussion)", "Tier 2 (For Information)"]
selectLookup = ["Non-Select", "Select"]

def get_meeting_id(meetings_df, formatted_value):
    """
    Retrieve the id of a meeting based on the Formatted column value.
    
    Parameters:
        meetings_df (pd.DataFrame): The DataFrame containing meeting data.
        formatted_value (str): The value in the Formatted column to search for.
        
    Returns:
        int or None: The id of the matching row, or None if not found.
    """
    matching_row = meetings_df.loc[meetings_df["Formatted"] == formatted_value]
    if not matching_row.empty:
        return int(matching_row["id"].iloc[0])
    return None

def get_meeting_date_title_index(meetings_df, meeting_id):
    result = meetings_df[meetings_df["id"] == np.int64(meeting_id)].index.tolist()
    return result[0] if result else 0

def get_select_string_value(select_flag):
    return "Select" if select_flag == 1 else "Non-Select"

def get_item_table_dict(meeting_id, form_data_dict):
    # Parse form inputs into a dictionary
    item_data = {
        "meetingId": meeting_id,
        "title": form_data_dict.get("item_title", "").strip(),
        "description": form_data_dict.get("item_description", "").strip(),
        "purpose": form_data_dict.get("item_purpose", ""),
        "tier": 1 if "Tier 1" in form_data_dict.get("item_purpose", "") else 2,
        "selectFlag": 1 if form_data_dict.get("select_flag", "Non-Select") == "Select" else 0,
        "duration": form_data_dict.get("duration", 0),
        "itemOwner": form_data_dict.get("item_owner", "").strip(),
        "additionalAttendees": ", ".join(form_data_dict.get("additional_attendees", [])),
    }
    return item_data

# Function to parse form inputs and create the item
def handle_form_submission(meeting_id, form_data_dict):
    # Call the create_item function
    item_data = get_item_table_dict(meeting_id, form_data_dict)
    system_data = {
        "status": Item_Status.PENDING.value,  # Default status
        "createdBy": "Admin",
        "createdOn": datetime.now().timestamp()
    }
    item_data.update(system_data)
    created_item = create_item(item_data)
    st.success(f"Item '{created_item['title']}' successfully created!")
    st.write(item_data)
    return created_item

# Function to parse form inputs and create the item
def handle_form_update(meeting_id, item_id, form_data_dict):
    item_data = get_item_table_dict(meeting_id, form_data_dict)
    # Call the update_item function
    updated_item = update_item(item_id, item_data)
    st.success(f"Item '{updated_item['title']}' successfully updated")
    st.write(item_data)
    return updated_item

def register_item_page():
    form_data_dict = item_details = {}
    # Parse the meeting_id from query parameters
    item_id = meeting_id = None
    register = update = None
    meetings = load_meeting_data()
    if st.query_params.get('meeting-id') is not None and st.query_params.get('id') is not None:
        meeting_id = st.query_params['meeting-id']
        item_id = st.query_params.get('id')
        item_details = get_item_by_id(item_id)

    formatted_data = [
        {"Formatted": f"{meeting['meetingTitle']} ({format_date(meeting['meetingDate'])})", "id": meeting["id"]}
        for meeting in meetings
    ]
    meetings_df = pd.DataFrame(formatted_data)

    # Display the meeting ID
    if item_id is None:
        st.title("Item Registration for HODM")
    else:
        st.title("Edit Item for HODM")

    # Meeting Item Form
    with st.form("register_item_form"):
        # Input fields
        if item_id is None:
            meeting_date_df = st.selectbox(    
                "Date of Meeting",
                options=meetings_df,
            )
            meeting_id = get_meeting_id(meetings_df, meeting_date_df)
        else:
            meeting_date_df = st.selectbox(
                "Date of Meeting",
                options=meetings_df,
                index=get_meeting_date_title_index(meetings_df, meeting_id)
            )

        form_data_dict["item_title"] = st.text_input("Item Title", placeholder="Enter the title of the item", value=item_details.get("title", ""))
        form_data_dict["item_description"] = st.text_area("Item Description", placeholder="Enter the item description", value=item_details.get("description", ""))
        
        form_data_dict["item_purpose"] = st.selectbox(
            "Item Purpose",
            options=purposeLookup,
            index=purposeLookup.index(item_details["purpose"]) if item_details.get("purpose") is not None else 0
        )
        
        form_data_dict["select_flag"] = st.selectbox(
            "Select or Non-Select",
            options=selectLookup,
            index=selectLookup.index(get_select_string_value(item_details["selectFlag"])) if item_details.get("selectFlag") is not None else 0
        )
        
        form_data_dict["duration"] = st.number_input("Duration (minutes)", min_value=5, max_value=30, step=5, value=item_details.get("duration", 5))
        form_data_dict["item_owner"] = st.text_input("Item Owner", placeholder="Enter the item owner's name", value=item_details.get("itemOwner", ""))
        
        print(item_details)
        # Dynamic input for additional attendees
        st.subheader("Additional Attendees")
        form_data_dict["additional_attendees"] = st.multiselect(
            "Add attendees",
            options=["Attendee 1", "Attendee 2", "Attendee 3", "Attendee 4"],
            placeholder="Type or select attendee names",
            default=item_details["additionalAttendees"].split(", ") if item_details.get("additionalAttendees") is not None else None
        )
        
        # Submit button
        _, button_col1 = st.columns([15,1])  # Equal width columns for buttons
        with button_col1:
            if item_id is None:
                register = st.form_submit_button("Register Item")
            else:
                update = st.form_submit_button("Update Item")

    # Process form submission
    if register:
        if meeting_id is not None:
            handle_form_submission(meeting_id, form_data_dict)
        else:
            st.error("Invalid Meeting ID: " + meeting_id)
    elif update:
        if meeting_id and item_id is not None:
            handle_form_update(meeting_id, item_id, form_data_dict)
        else:
            st.error("Invalid Item ID or Meeting ID: " + item_id + " " + meeting_id)

        

register_item_page()
