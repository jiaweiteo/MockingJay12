import streamlit as st
from collections import defaultdict
from pathlib import Path
import sqlite3
import pandas as pd
from dataclasses import dataclass

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB limit

@dataclass
class Attachment:
    id: int
    itemId: int
    filename: str
    fileType: str
    fileData: bytes

def connect_attachment_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent.parent / "database" / "attachment.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    if db_was_just_created:
        initialize_attachment_table(conn)

    return conn

def initialize_attachment_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_data BLOB NOT NULL,
        )
    """)
    conn.commit()

def save_attachment(item_id: int, uploaded_file):
    # Check file size
    file_data = uploaded_file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB")
    
    # Validate file type
    file_type = uploaded_file.type
    # allowed_types = ['application/pdf', 'application/msword', 
    #                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    #                 'text/plain']
    
    # if file_type not in allowed_types:
    #     raise ValueError("File type not allowed")
    
    try:
        with connect_attachment_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attachments (item_id, filename, file_type, file_data)
                VALUES (?, ?, ?, ?)
            """, (item_id, uploaded_file.name, file_type, file_data))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error saving attachment: {e}")
        return None

def get_attachments_for_item(item_id: int):
    with connect_attachment_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, file_type, file_data,
                    LENGTH(file_data) as file_size,
                    datetime('now') as upload_date
            FROM attachments
            WHERE item_id = ?
            ORDER BY filename
        """, (item_id,))
        return [dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()]

def delete_attachment(attachment_id: int) -> bool:
    try:
        with connect_attachment_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    
def delete_attachment_by_item_id(item_id: int) -> bool:
    try:
        with connect_attachment_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attachments WHERE item_id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False