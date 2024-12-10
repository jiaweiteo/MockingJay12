import streamlit as st

from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd


# -----------------------------------------------------------------------------
# Declare some useful functions.


def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "meeting.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    """Initializes the meeting table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meeting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meetingTitle TEXT,
            meetingDate TEXT,
            startTime TEXT,
            endTime TEXT,
            totalDuration INTEGER,
            slotsAvailable INTEGER,
            location TEXT,
            createdBy TEXT,
            createdOn INTEGER
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO meeting
            (meetingTitle, meetingDate, startTime, endTime, totalDuration, slotsAvailable, location, createdBy, createdOn)
        VALUES
            ('01/25', '2025-01-06', '15:00', '17:30', 150, 20, "Orchard", 'Jia Wei', 1733825082),
            ('01/25', '2025-01-23', '15:00', '17:30', 150, 20, "Yishun", 'Jia Wei', 1733825082),
            ('01/25', '2025-02-06', '15:00', '17:30', 150, 20, "Woodlands", 'Jia Wei', 1733825082),
            ('01/25', '2025-02-23', '15:00', '17:30', 150, 20, "Jurong", 'Jia Wei', 1733825082),
            ('01/25', '2025-03-06', '15:00', '17:30', 150, 20, "Boon Lay", 'Jia Wei', 1733825082),
            ('01/25', '2025-03-20', '15:00', '17:30', 150, 20, "Simei", 'Jia Wei', 1733825082)
        """
    )
    conn.commit()


def load_data(conn):
    """Loads the meeting data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM meeting")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "meetingTitle",
            "meetingDate",
            "startTime",
            "endTime",
            "totalDuration",
            "slotsAvailable",
            "location",
            "createdBy",
            "createdOn",
        ],
    )

    return df


def update_data(conn, df, changes):
    """Updates the meeting data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.meeting_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            """
            UPDATE meeting
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
                reorder_point = :reorder_point,
                description = :description
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO meeting
                (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )

    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM meeting WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )

    conn.commit()


# -----------------------------------------------------------------------------

"""
# :calendar: MockingJay

**This is a single-stop platform for managing HODM processes and progress**
"""

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")
else:
    st.toast("Retrieved data from Database.")

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        # "price": st.column_config.NumberColumn(format="$%.2f"),
        # "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key="meeting_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.meeting_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.meeting_table),
)

