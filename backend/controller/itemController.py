import streamlit as st
from collections import defaultdict
from pathlib import Path
import sqlite3
import pandas as pd
from dataclasses import dataclass

@dataclass
class MeetingItem:
    id: int
    meetingId: int
    title: str
    status: str
    description: str
    duration: int
    purpose: str
    tier: int
    selectFlag: int
    itemOwner: str
    additionalAttendees: str
    createdBy: str
    createdOn: int

def connect_item_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent.parent / "database" / "item.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    if db_was_just_created:
        initialize_item_table(conn)

    return conn

def initialize_item_table(conn):
    """Initializes the item table with dummy data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meetingId INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            purpose TEXT,
            tier INTEGER,
            selectFlag INTEGER,
            duration INTEGER,
            itemOwner TEXT,
            additionalAttendees TEXT,
            status TEXT,
            createdBy TEXT,
            createdOn INTEGER
        )
        """
    )
    conn.commit()


# Create item
def create_item(item_data):
    """
    Create a new item in the database.
    
    Parameters:
        item_data (dict): A dictionary containing the item's details.
        
    Returns:
        dict: The inserted item with its ID.
    """
    query = """
    INSERT INTO Item (meetingId, title, description, purpose, tier, selectFlag, duration, itemOwner, additionalAttendees, status, createdBy, createdOn)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        item_data["meetingId"],
        item_data["title"],
        item_data["description"],
        item_data["purpose"],
        item_data["tier"],
        item_data["selectFlag"],
        item_data["duration"],
        item_data["itemOwner"],
        item_data["additionalAttendees"],
        item_data["status"],
        item_data["createdBy"],
        item_data["createdOn"]
    )

    with connect_item_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        item_id = cursor.lastrowid
        item_data["id"] = item_id
    return item_data

# Read items by meetingId
def read_items(meeting_id):
    query = "SELECT * FROM Item WHERE meetingId = ?"
    
    with connect_item_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (meeting_id,))
        rows = cursor.fetchall()
        # Convert rows to list of dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

# Update item by id
def update_item(item_id, updated_data):
    if not updated_data:
        raise ValueError("Updates dictionary cannot be empty.")

    # Construct the SQL query dynamically based on the updates
    set_clause = ", ".join([f"{key} = ?" for key in updated_data.keys()])
    query = f"""
    UPDATE item
    SET {set_clause}
    WHERE id = ?
    """

    # Prepare the values for the query
    values = tuple(updated_data.values()) + (item_id,)

    # Connect to the database and execute the query
    try:
        with connect_item_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            print("Item successfully updated.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the item: {e}")

    conn.close()
    return get_item_by_id(item_id)

def update_agenda_table_data(df, changes):
    with connect_item_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if changes["edited_rows"]:
            deltas = st.session_state.agenda_editor["edited_rows"]
            rows = []
            for i, delta in deltas.items():
                row_dict = df.iloc[i].to_dict()
                row_dict.update(delta)
                rows.append(row_dict)

            cursor.executemany(
                """
                UPDATE item
                SET
                    title = :title,
                    description = :description,
                    purpose = :purpose,
                    tier = :tier,
                    duration = :duration,
                    itemOwner = :itemOwner,
                    additionalAttendees = :additionalAttendees
                    status = :status
                WHERE id = :id
                """,
                rows,
                )

        if changes["deleted_rows"]:
            cursor.executemany(
                "DELETE FROM item WHERE id = :id",
                ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
            )

        
        if changes["added_rows"]:
            cursor.executemany(
                """
                INSERT INTO item
                     (meetingId, title, description, purpose, tier, selectFlag, duration, itemOwner, additionalAttendees, status, createdBy, createdOn)
                VALUES
                    (:meetingId, :title, :description, :purpose, :tier, :selectFlag, :duration, :itemOwner, :additionalAttendees, :status, :createdBy, :createdOn)
                """,
                (defaultdict(lambda: None, row) for row in changes["added_rows"]),
            )

        conn.commit()
        conn.close()


# Helper function to fetch a single item by ID
def get_item_by_id(item_id):
    query = "SELECT * FROM Item WHERE id = ?"
    
    with connect_item_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (item_id,))
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
    return None

# Delete item by id
def delete_item(item_id):
    item = get_item_by_id(item_id)
    if not item:
        return None
    
    query = "DELETE FROM Item WHERE id = ?"
    
    with connect_item_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (item_id,))
        conn.commit()
    return item

# Retrieve items by meeting_id and sort them by purpose
def get_sorted_items_by_id(meeting_id):
    query = """
    SELECT * FROM Item
    WHERE meetingId = ?
    """
    
    # Priority order for sorting
    purpose_order = {
        "Tier 1 (For Approval)": 1,
        "Tier 1 (For Discussion)": 2,
        "Tier 2 (For Information)": 3,
    }
    
    with connect_item_db() as conn:
        df = pd.read_sql_query(query, conn, params=(meeting_id,))
        
    if df.empty:
        return []
    
    df["purpose_order"] = df["purpose"].map(purpose_order)
    sorted_df = df.sort_values(by="purpose_order").drop(columns=["purpose_order"])
    return sorted_df.to_dict(orient="records")

def get_total_duration(meeting_id: int) -> int:
    """
    Returns the total duration of all items for a given meeting ID.
    """
    with connect_item_db() as conn:
        query = "SELECT SUM(duration) AS total_duration FROM Item WHERE meetingId = ?;"
        result = conn.execute(query, (meeting_id,)).fetchone()
        return result[0] if result[0] is not None else 0  # Return 0 if no items are found
