from collections import defaultdict
from pathlib import Path
import sqlite3
import pandas as pd


# Mock data for full personnel database
def connect_personnel_db():
    """Connects to the personnel sqlite database."""
    DB_FILENAME = Path(__file__).parent / "personnel.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    return conn, db_was_just_created


def initialize_personnel_data(conn):
    """Initializes the personnel table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personnel (
            perNum INTEGER PRIMARY KEY,
            name TEXT,
            designation TEXT
        );
        """
    )

    cursor.execute(
        """
        INSERT INTO personnel
            (perNum, name, designation) 
        VALUES
            (32788, 'Diego Singleton', 'President'),
            (81316, 'Iyana Sweeney', 'BoardMember 1'),
            (95169, 'Jacey Douglas', 'BoardMember 2'),
            (28811, 'Fisher Taylor', 'BoardMember 3'),
            (93492, 'Serena Webster', 'BoardMember 4'),
            (41870, 'Graham Shields', 'BoardMember 5'),
            (59598, 'Jonathon Baxter', 'BoardMember 6'),
            (48246, 'Brylee Mcdaniel', 'BoardMember 7'),
            (87829, 'Kadence Donaldson', 'Chief Accountant'),
            (45387, 'Emilia Cooper', 'Chief Technology'),
            (14902, 'Demetrius Reese', 'Chief Corporate'),
            (10887, 'Bryson Gilbert', 'Chief HR'),
            (25616, 'Yosef Love', 'Director Accountant 1'),
            (30749, 'Sonny Figueroa', 'Director Accountant 2'),
            (8135, 'Alicia Kirk', 'Director Accountant 3'),
            (18642, 'Alicia Griffin', 'Director Technology 1'),
            (71433, 'Jackson Mcintosh', 'Director Technology 2'),
            (93449, 'Messiah Joseph', 'Director Technology 3'),
            (10584, 'Bianca Moran', 'Director Technology 4'),
            (32893, 'Presley Franklin', 'Director Corporate 1'),
            (69129, 'Marlon Fields', 'Director Corporate 2'),
            (81044, 'Melissa Moon', 'Director HR 1'),
            (48928, 'Kiara Bates', 'Director HR 2'),
            (90599, 'Kendall Choi', 'Head Gardening'),
            (36832, 'Oswaldo Bass', 'Head Landscape'),
            (2223, 'Javion Mayo', 'Head Manufacturing'),
            (12587, 'Katrina Kemp', 'Head Nurse'),
            (74729, 'Aurora Branch', 'Head Sales'),
            (41212, 'Rex Shaffer', 'Head Marketing'),
            (97132, 'Brett Roach', 'Head Communications'),
            (92664, 'Nico Hardy', 'Head Transport'),
            (54546, 'Layton Rowland', 'Manager Technology 1'),
            (54011, 'Maximo Huffman', 'Manager Technology 2'),
            (46528, 'Aidan Andrews', 'Manager Technology 3'),
            (96465, 'Jamison Rangel', 'Manager Technology 4'),
            (17206, 'Haleigh Schroeder', 'Manager Sales 1'),
            (91225, 'Emily Murray', 'Manager Sales 2'),
            (70880, 'Ashanti Cooley', 'Manager Nurse'),
            (44049, 'Brittany Giles', 'Manager Marketing'),
            (87176, 'Fisher Dickerson', 'Manager Coporate'),
            (74612, 'Monica Guerrero', 'Techology Engineer'),
            (49091, 'Imani Owen', 'Accountant'),
            (75790, 'Dylan Moran', 'Nurse'),
            (48140, 'Yazmin Nicholson', 'Doctor'),
            (98437, 'Lawson Sloan', 'Policeman'),
            (59511, 'Camila Collier', 'Salesman'),
            (56752, 'Pedro Heath', 'chauffeur'),
            (34388, 'Kadence Wheeler', 'Reporter');
        """
    )
    conn.commit()


def load_personnel_data():
    """Loads the personnel data from the database."""
    conn, db_was_just_created = connect_personnel_db()
    conn.row_factory = sqlite3.Row
    if db_was_just_created:
        initialize_personnel_data(conn)
    cursor = conn.cursor()
    return conn

def connect_attendance_db():
    """Connects to the attendance sqlite database."""

    DB_FILENAME = Path(__file__).parent / "attendance.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_secretariat_data(conn, personnel_conn):
    """Initializes the secretariat table with some data."""
    secretariat_perNum_list = [54546, 70880, 96465, 48140, 49091]
    cursor = conn.cursor()
    personnel_cursor= personnel_conn.cursor()
    personnel_query = "SELECT * FROM personnel where perNum in (" + ', '.join(['?']*len(secretariat_perNum_list)) + ")" 

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS secretariat (
            perNum INTEGER PRIMARY KEY,
            name TEXT,
            designation TEXT
        );
        """
    )

    personnel_cursor.execute(personnel_query,secretariat_perNum_list)
    data = personnel_cursor.fetchall()      
    
    for row in data:
        perNum, name, designation = row
        cursor.execute(
            """
            INSERT OR REPLACE INTO secretariat
                (perNum, name, designation)
            VALUES
                (?,?,?);
        """,
        (perNum, name, designation)
    )
    conn.commit()


def load_secretariat_data(personnelConn):
    """Loads the secretariat data from the database."""
    conn, db_was_just_created = connect_attendance_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('PRAGMA table_info(secretariat)')
    table_checker = cursor.fetchall()
    if len(table_checker) == 0:
        initialize_secretariat_data(conn,personnelConn)

    query = """
    SELECT *
    FROM secretariat
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
    except:
        return None
    
    conn.close()
    return data


def initialize_coremembers_data(conn, personnel_conn):
    """Initializes the secretariat table with some data."""
    coremembers_perNum_list = [32788, 81316, 95169, 28811, 93492, 41870, 59598, 48246, 87829, 45387, 14902, 10887, 25616, 30749, 8135, 18642, 71433, 93449, 10584, 32893, 69129, 81044, 48928]
    cursor = conn.cursor()
    personnel_cursor= personnel_conn.cursor()
    personnel_query = "SELECT * FROM personnel where perNum in (" + ', '.join(['?']*len(coremembers_perNum_list)) + ")" 

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coremembers (
            perNum INTEGER PRIMARY KEY,
            name TEXT,
            designation TEXT
        );
        """
    )

    personnel_cursor.execute(personnel_query,coremembers_perNum_list)
    data = personnel_cursor.fetchall()      

    for row in data:
        perNum, name, designation = row
        cursor.execute(
            """
            INSERT OR REPLACE INTO coremembers
                (perNum, name, designation)
            VALUES
                (?,?,?);
        """,
        (perNum, name, designation)
    )
    conn.commit()


def load_coremembers_data(personnelConn):
    """Loads the coremembers data from the database."""
    conn, db_was_just_created = connect_attendance_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(coremembers)')
    table_checker = cursor.fetchall()
    if len(table_checker) == 0:
        initialize_coremembers_data(conn,personnelConn)

    query = """
    SELECT *
    FROM coremembers
    """

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
    except:
        return None
    
    conn.close()
    return data


def add_table_member(table, perNum):
    if isinstance(perNum, int):
        perNum = perNum
    try:
        perNum = int(perNum)    
    except ValueError:    
        print('perNum needs to be integer!')
        exit()
    
    table = str(table)

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    personnel_conn, personnel_db_was_just_created = connect_personnel_db()

    attendance_cursor = attendance_conn.cursor()
    personnel_cursor = personnel_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info({table})")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print(f'Table: {table} not found in database!')
        exit()

    personnel_select_query = "SELECT * FROM personnel WHERE perNum == ?"
    personnel_cursor.execute(personnel_select_query,(perNum,))
    data = personnel_cursor.fetchall()

    if len(data)>0:
        for row in data:
            perNum, name, designation = row
    else:
        print(f'No personnel with perNum {perNum}')
        exit()

    insert_query = f"INSERT OR REPLACE INTO {table} (perNum, name, designation) values (?,?,?)"
    attendance_cursor.execute(insert_query, (perNum, name, designation))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) inserted into {table}")   
    attendance_conn.commit()
    attendance_conn.close()
    personnel_conn.close()


def remove_table_member(table, perNum):
    perNum = int(perNum)
    if not type(perNum) is int:
        raise TypeError('perNum needs to be integer!')
    if not type(table) is str:
        raise TypeError('table needs to be string!')

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info({table})")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print('No such table!')
        exit()

    delete_query = f"DELETE from {table} WHERE perNum == ?"
    attendance_cursor.execute(delete_query, (perNum,))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) deleted from {table}")
    attendance_conn.commit()
    attendance_conn.close()
