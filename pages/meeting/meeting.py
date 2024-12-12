import streamlit as st
from backend.controller.meetingController import fetch_meeting_by_id, fetch_upcoming_meeting, delete_meeting
from backend.controller.itemController import get_sorted_items_by_id, delete_item
from datetime import datetime
from utils.dateUtils import *
from utils.constants import Role

def get_status_color(status):
    """
    Return the color code for the given status.
    """
    status_colors = {
        "Pending": "blue",
        "Registered": "green",
        "Waitlist": "yellow",
        "Rejected": "red",
    }
    return status_colors.get(status, "gray")  # Default to gray for unknown statuses

def display_items(items):
    if not items:
        st.info("No items found for this meeting.")
        return
    
    # Display items as cards
    for item in items:
        status_color = get_status_color(item["status"])
        with st.container():
            col1, col2, _ = st.columns([1, 1, 1])
            with col1:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #f9f9f9;">
                        <h4 style="margin: 0; color: #2c3e50;">{item['title']}</h4>
                        <p style="margin: 4px 0; color: {status_color};"><strong>Status:</strong> {item['status']}</p>
                        <p style="margin: 4px 0;"><strong>Description:</strong> {item['description']}</p>
                        <p style="margin: 4px 0;"><strong>Purpose:</strong> {item['purpose']}</p>
                        <p style="margin: 4px 0;"><strong>Duration:</strong> {item['duration']} minutes</p>
                        <p style="margin: 4px 0;"><strong>Owner:</strong> {item['itemOwner']}</p>
                        <p style="margin: 4px 0;"><strong>Additional Attendees:</strong> {item['additionalAttendees'] if item['additionalAttendees'] else "-"}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.link_button(label="Edit Item", url=f"/item-form?meeting-id={item['meetingId']}&id={item['id']}", icon="📝")
                if st.button(f"Delete Item", key=item["id"], icon='🗑️'):
                    st.session_state.delete_item = item
            

def confirm_delete_meeting(meeting_id):
    delete_meeting(meeting_id)
    st.rerun()

def confirm_delete_item(item_id, title):
    delete_item(item_id)
    st.success(f"Item '{title}' deleted successfully.")
    st.rerun()


@st.dialog("Delete Meeting")
def handle_delete_meeting(meeting_id, title):
    st.markdown(
        f"""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">Are you sure you want to delete {title} HODM meeting?</h4>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Delete"):
        confirm_delete_meeting(meeting_id)

@st.dialog("Delete Item")
def handle_delete_item(item_id, title):
    st.markdown(
        f"""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                <h4 style="margin: 0; color: #333;">Are you sure you want to delete {title} item?</h4>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Delete"):
        confirm_delete_item(item_id, title)


def display_meeting():
    meeting_id = None
    st.session_state.delete_meeting_modal = False
    st.session_state.delete_item = None

    if st.query_params.get('id') is not None:
        meeting_id = st.query_params['id']
        meeting_details = fetch_meeting_by_id(meeting_id)
    else:
        meeting_details = fetch_upcoming_meeting()
        meeting_id = meeting_details['id']


    if meeting_details is None:
        st.title("No Meeting found. Invalid Meeting ID: " + meeting_id)
    else:
        # Convert UNIX timestamp to human-readable format
        created_on_date = datetime.fromtimestamp(meeting_details["createdOn"]).strftime("%Y-%m-%d %H:%M:%S")

        # Page title
        st.title(meeting_details["meetingTitle"] + " HODM Meeting")
        st.subheader(meeting_details["description"])

        # Display meeting information
        with st.container():
            
            # Create two columns for better layout
            col1, col2 = st.columns(2)
            
            # Left column content
            with col1:
                st.subheader("Details", divider="green")
                st.write(f"**Date:** {format_date(meeting_details['meetingDate'])}")
                st.write(f"**Time:** {meeting_details['startTime']} - {meeting_details['endTime']}")
                st.write(f"**Location:** {meeting_details['location']}")
                st.write(f"**Created By:** {meeting_details['createdBy']} (Created on {created_on_date})")
                st.markdown('</div>', unsafe_allow_html=True)

                if st.session_state.role == Role.SECRETARIAT.value:
                    col3, col4 = st.columns([1,3])
                    with col3:
                        st.link_button(label="Edit Meeting", url=f"/meeting-form?id={meeting_details['id']}", icon="📝")
                    with col4:
                        if st.button("Delete Meeting", key=f"meetingId={meeting_id}", icon='🗑️'):
                            st.session_state.delete_meeting_modal = True

            # Right column content
            with col2:
                st.subheader("Demand", divider=True)
                st.write(f"**Duration:** {meeting_details['totalDuration']} minutes")
                st.write(f"**Time Taken:** {meeting_details['minutesTaken']}")
                st.write(f"**Time Left:** {meeting_details['minutesLeft']}")
                st.progress(meeting_details["minutesTaken"] / meeting_details['totalDuration'])
                st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.delete_meeting_modal:
            handle_delete_meeting(meeting_id, meeting_details["meetingTitle"])

        with st.container():
            st.subheader("Items Registered", divider="orange")
            st.link_button(label="Register New Item", url=f"/item-form?id={meeting_details['id']}", icon="📖")
            display_items(get_sorted_items_by_id(meeting_id))


        if st.session_state.delete_item is not None:
            print(st.session_state.delete_item)
            item = st.session_state.delete_item
            handle_delete_item(item["id"], item['title'])

display_meeting()