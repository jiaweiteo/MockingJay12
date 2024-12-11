from collections import defaultdict
from pathlib import Path
import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# Declare some useful functions.


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
            totalSlots INTEGER,
            slotsTaken INTEGER,
            location TEXT,
            createdBy TEXT,
            createdOn INTEGER
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO meeting
            (meetingTitle, meetingDate, description, startTime, endTime, totalDuration, totalSlots, slotsTaken, location, createdBy, createdOn)
        VALUES
            ('01/25', '2025-01-05', 'Tier 1 & Tier 2 Slots Available', '15:00', '17:30', 150, 20, 8, "Orchard", 'Jia Wei', 1733825082),
            ('02/25', '2025-01-23', 'Tier 1 Slots Left', '15:00', '17:30', 150, 20, 3, "Yishun", 'Jia Wei', 1733825082),
            ('03/25', '2025-02-06', 'Tier 2 Slots Left', '15:00', '17:30', 150, 20, 15, "Woodlands", 'Jia Wei', 1733825082),
            ('04/25', '2025-02-23', 'Almost Full', '15:00', '17:30', 150, 20, 2, "Jurong", 'Jia Wei', 1733825082),
            ('05/25', '2025-03-06', 'Test', '15:00', '17:30', 150, 20, 20, "Boon Lay", 'Jia Wei', 1733825082),
            ('06/25', '2025-03-20', 'No Slots Left', '15:00', '17:30', 150, 20, 0, "Simei", 'Jia Wei', 1733825082)
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

    try:
        cursor.execute("SELECT * FROM meeting")
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

# def update_meeting_data(conn, df, changes):
#     """Updates the meeting data in the database."""
#     cursor = conn.cursor()

#     if changes["edited_rows"]:
#         deltas = st.session_state.meeting_table["edited_rows"]
#         rows = []

#         for i, delta in deltas.items():
#             row_dict = df.iloc[i].to_dict()
#             row_dict.update(delta)
#             rows.append(row_dict)

#         cursor.executemany(
#             """
#             UPDATE meeting
#             SET
#                 item_name = :item_name,
#                 price = :price,
#                 units_sold = :units_sold,
#                 units_left = :units_left,
#                 cost_price = :cost_price,
#                 reorder_point = :reorder_point,
#                 description = :description
#             WHERE id = :id
#             """,
#             rows,
#         )

#     if changes["added_rows"]:
#         cursor.executemany(
#             """
#             INSERT INTO meeting
#                 (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
#             VALUES
#                 (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
#             """,
#             (defaultdict(lambda: None, row) for row in changes["added_rows"]),
#         )

#     if changes["deleted_rows"]:
#         cursor.executemany(
#             "DELETE FROM meeting WHERE id = :id",
#             ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
#         )

#     conn.commit()


# -----------------------------------------------------------------------------

