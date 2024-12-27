from pathlib import Path
import sqlite3
# from collections import defaultdict
# import pandas as pd
from dataclasses import dataclass
import streamlit as st

@dataclass
class Meeting:
    id: int
    meetingTitle: str
    meetingDate: str
    description: str
    startTime: str
    endTime: str
    totalDuration: int
    minutesLeft: int
    minutesTaken: int
    location: str
    createdBy: str
    createdOn: int
    status: str

def connect_meeting_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent.parent / "database" / "meeting.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_meeting_data(conn):
    """Initializes the meeting table with dummy data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meeting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meetingTitle TEXT,
            meetingDate TEXT,
            description TEXT,
            startTime TEXT,
            endTime TEXT,
            totalDuration INTEGER,
            minutesLeft INTEGER,
            minutesTaken INTEGER,
            location TEXT,
            createdBy TEXT,
            createdOn INTEGER,
            status TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO meeting
            (meetingTitle, meetingDate, description, startTime, endTime, totalDuration, minutesLeft, minutesTaken, location, createdBy, createdOn, status)
        VALUES
            ('01/25', '2025-01-05', 'Tier 1 & Tier 2 Slots Available', '15:00', '17:30', 150, 30, 120, "Orchard", 'Jia Wei', 1733825082, "Curation"),
            ('02/25', '2025-01-23', 'Tier 1 Slots Left', '15:00', '17:30', 150, 45, 105, "Yishun", 'Jia Wei', 1733825082, "Curation"),
            ('03/25', '2025-02-06', 'Tier 2 Slots Left', '15:00', '17:30', 150, 60, 90, "Woodlands", 'Jia Wei', 1733825082, "Curation"),
            ('04/25', '2025-02-23', 'Almost Full', '15:00', '17:30', 150, 150, 0, "Jurong", 'Jia Wei', 1733825082, "Curation"),
            ('05/25', '2025-03-06', 'Test', '15:00', '17:30', 150, 0, 150, "Boon Lay", 'Jia Wei', 1733825082, "Curation"),
            ('06/25', '2025-03-20', 'No Slots Left', '15:00', '17:30', 150, 100, 50, "Simei", 'Jia Wei', 1733825082, "Curation")
        """
    )
    conn.commit()


def load_meeting_data():
    conn, db_was_just_created = connect_meeting_db()
    conn.row_factory = sqlite3.Row
    if db_was_just_created:
        initialize_meeting_data(conn)

    """Loads the meeting data from the database."""
    cursor = conn.cursor()

    query = """
    SELECT *
    FROM meeting
    WHERE meetingDate >= DATE('now')
    ORDER BY meetingDate ASC, startTime ASC
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
    except:
        return None
    
    conn.close()
    return data

def load_past_meeting_data():
    conn, _ = connect_meeting_db()
    conn.row_factory = sqlite3.Row

    """Loads the meeting data from the database."""
    cursor = conn.cursor()

    query = """
    SELECT *
    FROM meeting
    WHERE meetingDate < DATE('now')
    ORDER BY meetingDate ASC, startTime ASC
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
    except:
        return None
    
    conn.close()
    return data

# Function to fetch a specific meeting by ID
def fetch_meeting_by_id(meeting_id):
    conn, _ = connect_meeting_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meeting WHERE id = ?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def fetch_upcoming_meeting():
    conn, _ = connect_meeting_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM meeting
    WHERE meetingDate >= DATE('now')
    ORDER BY meetingDate ASC, startTime ASC
    LIMIT 1;
    """
    cursor.execute(query)
    row = cursor.fetchone()

    # Close the connection
    conn.close()
    # Return the result as a dictionary
    return dict(row) if row else None

def create_meeting(meeting_details):
    required_keys = [
        "meetingTitle", "meetingDate", "description", "startTime", "endTime",
        "totalDuration", "minutesLeft", "minutesTaken", "location", "createdBy", "createdOn", "status"
    ]

    # Validate that all required keys are present
    for key in required_keys:
        if key not in meeting_details:
            raise ValueError(f"Missing required field: {key}")

    # SQL query to insert a new meeting
    query = """
    INSERT INTO meeting (
        meetingTitle, meetingDate, description, startTime, endTime,
        totalDuration, minutesLeft, minutesTaken, location, createdBy, createdOn, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Extract values from meeting_details dictionary
    values = tuple(meeting_details[key] for key in required_keys)

    # Connect to the database and execute the query
    try:
        conn, _ = connect_meeting_db()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        meeting_id = cursor.lastrowid
        print("Meeting successfully created.")
        st.toast("Meeting successfully created.")
        conn.close()
        return meeting_id
    except sqlite3.Error as e:
        print(f"An error occurred while inserting the meeting: {e}")
    
    conn.close()

def update_meeting(meeting_id, updates):
    if not updates:
        raise ValueError("Updates dictionary cannot be empty.")

    # Construct the SQL query dynamically based on the updates
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    query = f"""
    UPDATE meeting
    SET {set_clause}
    WHERE id = ?
    """

    # Prepare the values for the query
    values = tuple(updates.values()) + (meeting_id,)

    # Connect to the database and execute the query
    try:
        conn, _ = connect_meeting_db()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        print("Meeting successfully updated.")
        st.toast("Meeting successfully updated.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the meeting: {e}")

    conn.close()
    return meeting_id

def update_meeting_status(meeting_id, new_status):
    if not new_status:
        raise ValueError("new_status cannot be empty.")

    # Construct the SQL query dynamically based on the updates
    query = f"""
    UPDATE meeting
    SET status="{new_status}"
    WHERE id = ?
    """
    # Connect to the database and execute the query
    try:
        conn, _ = connect_meeting_db()
        cursor = conn.cursor()
        cursor.execute(query, (meeting_id,))
        conn.commit()
        print("Meeting Agenda Status successfully updated.")
        st.toast("Meeting Agenda Status successfully updated.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the meeting status: {e}")

    conn.close()


def delete_meeting(meeting_id):
    query = """
    DELETE FROM meeting
    WHERE id = ?
    """

    try:
        conn, _ = connect_meeting_db()
        cursor = conn.cursor()
        cursor.execute(query, (meeting_id,))
        conn.commit()
        print("Meeting successfully deleted.")
        st.toast("Meeting successfully deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred while deleting the meeting: {e}")

    conn.close()
