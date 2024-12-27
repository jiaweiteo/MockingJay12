import numpy as np
import pandas as pd
import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, load_meeting_data
from backend.controller.itemController import create_item, get_item_by_id, update_item
from backend.controller.attachmentsController import save_attachment, get_attachments_for_item, delete_attachment
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras import stylable_container
from utils.dateUtils import format_date
from utils.constants import Item_Status, Purpose_Lookup
import humanize

purposeLookup = [f":blue[{Purpose_Lookup.APPROVAL.value}]", f":blue[{Purpose_Lookup.DISCUSSION.value}]", f":orange[{Purpose_Lookup.INFO.value}]"]
selectLookup = ["Non-Select", "Select"]


st.markdown("""
<style>
:has(label input[tabindex="0"][type="radio"][value="2"]) div[data-testid="stColumn"] div.st-key-duration {
    display: none;
}
</style>
""", unsafe_allow_html=True)


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
        "duration": 0 if "Tier 2" in form_data_dict.get("item_purpose", "") else form_data_dict.get("duration", 0),
        "itemOwner": form_data_dict.get("item_owner", "").strip(),
        "additionalAttendees": ", ".join(form_data_dict.get("additional_attendees", [])),
    }
    return item_data

st.session_state.uploaded_files = None
def upload_attachments(item_id):
    if st.session_state.uploaded_files:
        for file in st.session_state.uploaded_files:
            # Check if file is already uploaded
            existing_files = get_attachments_for_item(item_id)
            if any(file.name == existing["filename"] for existing in existing_files):
                st.warning(f"File {file.name} already exists! Not saving this file.")
            else:
                save_attachment(item_id, file)
                st.success(f"Successfully uploaded {file.name}")
    st.session_state.uploaded_files = None

# Function to parse form inputs and create the item
def handle_form_submission(meeting_id, form_data_dict):
    # Call the create_item function
    item_data = get_item_table_dict(meeting_id, form_data_dict)
    system_data = {
        "status": Item_Status.REGISTERED.value,  # Default status
        "createdBy": "Admin",
        "createdOn": datetime.now().timestamp()
    }
    item_data.update(system_data)
    created_item = create_item(item_data)
    if st.session_state.uploaded_files is not None:
        upload_attachments(created_item["id"])

    st.success(f"Item '{created_item['title']}' successfully created!")
    st.write(item_data)
    return created_item


# Function to parse form inputs and create the item
def handle_form_update(meeting_id, item_id, form_data_dict):
    item_data = get_item_table_dict(meeting_id, form_data_dict)
    # Call the update_item function
    updated_item = update_item(item_id, item_data)
    if st.session_state.uploaded_files is not None:
        upload_attachments(updated_item["id"])

    st.success(f"Item '{updated_item['title']}' successfully updated")
    st.write(item_data)
    return updated_item


@st.fragment
def register_item_page():
    form_data_dict = item_details = {}
    # Parse the meeting_id from query parameters
    global item_id
    global meeting_id
    attachments = None
    register = update = None
    meetings = load_meeting_data()
    if st.query_params.get('meeting-id') is not None:
        meeting_id = st.query_params['meeting-id']

    if st.query_params.get('id') is not None:
        item_id = st.query_params.get('id')
        
    if item_id is not None:
        item_details = get_item_by_id(item_id)
        attachments = get_attachments_for_item(item_id)

    formatted_data = [
        {"Formatted": f"{meeting['meetingTitle']} ({format_date(meeting['meetingDate'])})", "id": meeting["id"]}
        for meeting in meetings
    ]
    meetings_df = pd.DataFrame(formatted_data)

    # Display the meeting ID
    if item_id is None:
        st.title("Item Registration for DM")
    else:
        st.title("Edit Item for DM")
    
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

    item_details_col, _ = st.columns([4, 2])
    with item_details_col:
        with st.form("register_item_form"):
            if meeting_id is None:
                meeting_date_df = st.selectbox(    
                    "Date of Meeting",
                    options=meetings_df,
                    index=None
                )
                meeting_id = get_meeting_id(meetings_df, meeting_date_df)
            else:
                meeting_date_df = st.selectbox(
                    "Date of Meeting",
                    options=meetings_df,
                    index=get_meeting_date_title_index(meetings_df, meeting_id)
                )

            form_data_dict["item_title"] = st.text_input(
                "Item Title",
                placeholder="Enter the title of the item",
                value=item_details.get("title", "")
            )
            
            form_data_dict["item_description"] = st.text_area(
                "Item Description",
                placeholder="Enter the item description",
                value=item_details.get("description", "")
            )

            col_purpose, col_duration = st.columns([3, 2], border=True)

            with col_purpose:
                purpose = st.radio(
                    "Item Purpose",
                    purposeLookup,
                    index=purposeLookup.index(item_details.get("purpose")) if item_details.get("purpose") is not None else 0,
                    key="purpose"
                )
                form_data_dict["item_purpose"] = purpose
            
            with col_duration:
                form_data_dict["duration"] = st.number_input(
                        "Duration (minutes)",
                        min_value=0,
                        max_value=30,
                        step=5,
                        value=item_details.get("duration", 15),
                        key="duration"
                    )
            
            col_owner, col_select = st.columns([3, 2], border=True)

            with col_owner:
                label = 'Presenter'
                placeholder = "Enter the presenter's name"               
                form_data_dict["item_owner"] = st.text_input(label, placeholder=placeholder, value=item_details.get("itemOwner", ""))
                        
            with col_select:
                form_data_dict["select_flag"] = st.checkbox("Select?")
        
            form_data_dict["additional_attendees"] = st.multiselect(
                "Add attendees",
                options=["Attendee 1", "Attendee 2", "Attendee 3", "Attendee 4"],
                placeholder="Type or select attendee names",
                default=item_details["additionalAttendees"].split(", ") if item_details.get("additionalAttendees") is not None else None,
                key="attendees"
            )

            st.session_state.uploaded_files = st.file_uploader(
                "Upload Attachments", accept_multiple_files=True
            )

            # Display attachments in a table with actions
            if item_id is None:
                register = st.form_submit_button("Register Item", type="primary", use_container_width=True)
            else:
                update = st.form_submit_button("Update Item", type="primary", use_container_width=True)
        
        if attachments is not None:
            st.subheader("Attachments")
            for attachment in attachments:
                with st.container():                   
                    cols = st.columns([5, 1, 1, 1])
                    
                    # Column 1: Filename
                    cols[0].text(attachment['filename'])
                    
                    # Column 2: File size
                    file_size = humanize.naturalsize(attachment['file_size'])
                    cols[1].text(file_size)
                    
                    # Column 3: Download button
                    file_data = attachment['file_data']  # Get file data
                    cols[2].download_button(
                        "📥 Download",
                        data=file_data,
                        file_name=attachment['filename'],
                        mime=attachment['file_type'],
                        key=f"download_{attachment['id']}"
                    )
                    
                    # Column 4: Delete button
                    if cols[3].button("🗑️", key=f"delete_{attachment['id']}"):
                        st.session_state.delete_confirmation = attachment['id']

                    if st.session_state.delete_confirmation == attachment["id"]:
                        st.warning(f"Are you sure you want to delete {attachment['filename']}?")
                        col1, col2 = st.columns([1, 1])
                        
                        if col1.button("Yes, delete", key=f"confirm_yes_{attachment['id']}"):
                            if delete_attachment(attachment['id']):
                                st.success("File deleted successfully!")
                                st.session_state.delete_confirmation = None
                                st.rerun()
                            else:
                                st.error("Failed to delete file")
                                st.session_state.delete_confirmation = None
                        
                        if col2.button("No, cancel", key=f"confirm_no_{attachment['id']}"):
                            st.session_state.delete_confirmation = None
                            st.rerun()

                st.divider()

    # Process form submission
    if register:
        if meeting_id is not None:
            created_item = handle_form_submission(meeting_id, form_data_dict)
            item_id = created_item["id"]
            meeting_id = created_item["meetingId"]
            st.rerun(scope="fragment")
        else:
            st.error("Invalid Meeting ID: " + meeting_id)
    elif update:
        if meeting_id and item_id is not None:
            handle_form_update(meeting_id, item_id, form_data_dict)
            st.rerun(scope="fragment")

        else:
            st.error("Invalid Item ID or Meeting ID: " + item_id + " " + meeting_id)

st.session_state.delete_confirmation = None
item_id = meeting_id = None
register_item_page()
