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
            designation TEXT,
            role TEXT check (role in ('HOD','Permanent',''))
        );
        """
    )

    cursor.execute(
        """
        INSERT INTO personnel
            (perNum, name, designation,role) 
        VALUES
            (32788, 'Diego Singleton', 'President', 'HOD'),
            (81316, 'Iyana Sweeney', 'BoardMember 1', 'HOD'),
            (95169, 'Jacey Douglas', 'BoardMember 2', 'HOD'),
            (28811, 'Fisher Taylor', 'BoardMember 3', 'HOD'),
            (93492, 'Serena Webster', 'BoardMember 4', 'HOD'),
            (41870, 'Graham Shields', 'BoardMember 5', 'HOD'),
            (59598, 'Jonathon Baxter', 'BoardMember 6', 'HOD'),
            (48246, 'Brylee Mcdaniel', 'BoardMember 7', 'HOD'),
            (87829, 'Kadence Donaldson', 'Chief Accountant', 'HOD'),
            (45387, 'Emilia Cooper', 'Chief Technology', 'HOD'),
            (14902, 'Demetrius Reese', 'Chief Corporate', 'HOD'),
            (10887, 'Bryson Gilbert', 'Chief HR', 'HOD'),
            (25616, 'Yosef Love', 'Director Accountant 1', 'HOD'),
            (30749, 'Sonny Figueroa', 'Director Accountant 2', 'HOD'),
            (8135, 'Alicia Kirk', 'Director Accountant 3', 'HOD'),
            (18642, 'Alicia Griffin', 'Director Technology 1', 'HOD'),
            (71433, 'Jackson Mcintosh', 'Director Technology 2', 'HOD'),
            (93449, 'Messiah Joseph', 'Director Technology 3', 'HOD'),
            (10584, 'Bianca Moran', 'Director Technology 4', 'Permanent'),
            (32893, 'Presley Franklin', 'Director Corporate 1', 'Permanent'),
            (69129, 'Marlon Fields', 'Director Corporate 2', 'Permanent'),
            (81044, 'Melissa Moon', 'Director HR 1', 'Permanent'),
            (48928, 'Kiara Bates', 'Director HR 2', 'Permanent'),
            (90599, 'Kendall Choi', 'Head Gardening', ''),
            (36832, 'Oswaldo Bass', 'Head Landscape', ''),
            (2223, 'Javion Mayo', 'Head Manufacturing', ''),
            (12587, 'Katrina Kemp', 'Head Nurse', ''),
            (74729, 'Aurora Branch', 'Head Sales', ''),
            (41212, 'Rex Shaffer', 'Head Marketing', ''),
            (97132, 'Brett Roach', 'Head Communications', ''),
            (92664, 'Nico Hardy', 'Head Transport', ''),
            (54546, 'Layton Rowland', 'Manager Technology 1',''),
            (54011, 'Maximo Huffman', 'Manager Technology 2',''),
            (46528, 'Aidan Andrews', 'Manager Technology 3',''),
            (96465, 'Jamison Rangel', 'Manager Technology 4',''),
            (17206, 'Haleigh Schroeder', 'Manager Sales 1',''),
            (91225, 'Emily Murray', 'Manager Sales 2',''),
            (70880, 'Ashanti Cooley', 'Manager Nurse',''),
            (44049, 'Brittany Giles', 'Manager Marketing',''),
            (87176, 'Fisher Dickerson', 'Manager Coporate',''),
            (74612, 'Monica Guerrero', 'Techology Engineer',''),
            (49091, 'Imani Owen', 'Accountant',''),
            (75790, 'Dylan Moran', 'Nurse',''),
            (48140, 'Yazmin Nicholson', 'Doctor',''),
            (98437, 'Lawson Sloan', 'Policeman',''),
            (59511, 'Camila Collier', 'Salesman',''),
            (56752, 'Pedro Heath', 'chauffeur',''),
            (34388, 'Kadence Wheeler', 'Reporter','');
        """
    )
    conn.commit()


def load_personnel_data():
    """Loads the personnel data from the database."""
    conn, db_was_just_created = connect_personnel_db()
    conn.row_factory = sqlite3.Row
    if db_was_just_created:
        initialize_personnel_data(conn)
    return conn

def connect_attendance_db():
    """Connects to the sqlite database."""

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
    personnel_query = "SELECT perNum, name, designation FROM personnel where perNum in (" + ', '.join(['?']*len(secretariat_perNum_list)) + ")" 

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
    conn.close()


def initialize_coremembers_data(conn, personnel_conn):
    """Initializes the coremembers table with some data."""
    coremembers_perNum_list = [32788, 81316, 95169, 28811, 93492, 41870, 59598, 48246, 87829, 45387, 14902, 10887, 25616, 30749, 8135, 18642, 71433, 93449, 10584, 32893, 69129, 81044, 48928]
    cursor = conn.cursor()
    personnel_cursor= personnel_conn.cursor()
    personnel_query = "SELECT perNum, name, designation, role FROM personnel where perNum in (" + ', '.join(['?']*len(coremembers_perNum_list)) + ")" 

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coremembers (
            perNum INTEGER PRIMARY KEY,
            name TEXT,
            designation TEXT,
            role TEXT check(role in ('HOD','Permanent'))
        );
        """
    )

    personnel_cursor.execute(personnel_query,coremembers_perNum_list)
    data = personnel_cursor.fetchall()      

    for row in data:
        perNum, name, designation, role = row
        cursor.execute(
            """
            INSERT OR REPLACE INTO coremembers
                (perNum, name, designation, role)
            VALUES
                (?,?,?,?);
        """,
        (perNum, name, designation, role)
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
    conn.close()



def add_or_update_table_member(table, perNum):
    # Add member into secretariat or coremembers table
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

    personnel_select_query = "SELECT perNum, name, designation FROM personnel WHERE perNum == ?"
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
    # Remove member from secretariat or coremembers table
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


def initialize_item_owners_table(conn):
    """Initializes the item_owners table."""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS item_owners (
            perNum INTEGER PRIMARY KEY,
            name TEXT,
            designation TEXT,
            meeting_id NOT NULL,
            item_id not NULL
        );
        """
    )
    conn.commit()
    conn.close()


def load_item_owners_table():
    """Loads the item_owners table into the database."""
    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_conn.row_factory = sqlite3.Row
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute('PRAGMA table_info(item_owners)')
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        initialize_item_owners_table(attendance_conn)
    attendance_conn.close()
 


def add_or_update_item_owners(meeting_id, item_id, perNum):
    # Adding item owner into item_owners
    if isinstance(perNum, int):
        perNum = perNum
    try:
        perNum = int(perNum)    
    except ValueError:    
        print('perNum needs to be integer!')
        exit()

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    personnel_conn, personnel_db_was_just_created = connect_personnel_db()

    attendance_cursor = attendance_conn.cursor()
    personnel_cursor = personnel_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info(item_owners)")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print(f'Table: item_owners not found in database!')
        exit()

    personnel_select_query = "SELECT perNum, name, designation FROM personnel WHERE perNum == ?"
    personnel_cursor.execute(personnel_select_query,(perNum,))
    data = personnel_cursor.fetchall()

    if len(data)>0:
        for row in data:
            perNum, name, designation = row
    else:
        print(f'No personnel with perNum {perNum}')
        exit()

    insert_query = f"INSERT OR REPLACE INTO item_owners (perNum, name, designation,meeting_id, item_id) values (?,?,?,?,?)"
    attendance_cursor.execute(insert_query, (perNum, name, designation,meeting_id, item_id))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) inserted into item_owners")   
    attendance_conn.commit()
    attendance_conn.close()
    personnel_conn.close()


def remove_item_owners(meeting_id, item_id, perNum):
    # Removing an item owner from item_owners
    if isinstance(perNum, int):
        perNum = perNum
    try:
        perNum = int(perNum)    
    except ValueError:    
        print('perNum needs to be integer!')
        exit()

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info(item_owners)")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print(f'Table: item_owners not found in database!')
        exit()

    delete_query = f"DELETE from item_owners WHERE perNum == ? and meeting_id== ? and item_id == ?"
    attendance_cursor.execute(delete_query, (perNum, meeting_id, item_id,))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) deleted from item_owners")   
    attendance_conn.commit()
    attendance_conn.close()


def initialize_additional_attendees_table(conn):
    """Initializes the non-select attendance table."""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS additional_attendees (
            perNum INTEGER,
            name TEXT,
            designation TEXT,
            meeting_id NOT NULL,
            item_id not NULL
        );
        """
    )
    conn.commit()
    conn.close()


def load_additional_attendees_table():
    """Loads the additional attendees into the database."""
    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_conn.row_factory = sqlite3.Row
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute('PRAGMA table_info(additional_attendees)')
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        initialize_additional_attendees_table(attendance_conn)
    attendance_conn.close()



def add_additional_attendees(meeting_id, item_id, perNum):
    """ Adds additional attendees into additional_attendees table"""
    if isinstance(perNum, int):
        perNum = perNum
    try:
        perNum = int(perNum)    
    except ValueError:    
        print('perNum needs to be integer!')
        exit()

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    personnel_conn, personnel_db_was_just_created = connect_personnel_db()

    attendance_cursor = attendance_conn.cursor()
    personnel_cursor = personnel_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info(additional_attendees)")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print(f'Table: additional_attendees not found in database!')
        exit()

    personnel_select_query = "SELECT perNum, name, designation FROM personnel WHERE perNum == ?"
    personnel_cursor.execute(personnel_select_query,(perNum,))
    data = personnel_cursor.fetchall()

    if len(data)>0:
        for row in data:
            perNum, name, designation = row
    else:
        print(f'No personnel with perNum {perNum}')
        exit()

    insert_query = f"INSERT OR REPLACE INTO additional_attendees (perNum, name, designation,meeting_id, item_id) values (?,?,?,?,?)"
    attendance_cursor.execute(insert_query, (perNum, name, designation,meeting_id, item_id))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) inserted into additional_attendees")   
    attendance_conn.commit()
    attendance_conn.close()
    personnel_conn.close()


def remove_additional_attendees(meeting_id, item_id, perNum):
    """ Removing additional attendees from additional_attendees table"""
    if isinstance(perNum, int):
        perNum = perNum
    try:
        perNum = int(perNum)    
    except ValueError:    
        print('perNum needs to be integer!')
        exit()

    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute(f"PRAGMA table_info(additional_attendees)")
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        print(f'Table: additional_attendees not found in database!')
        exit()

    delete_query = f"DELETE from additional_attendees WHERE perNum == ? and meeting_id== ? and item_id == ?"
    attendance_cursor.execute(delete_query, (perNum, meeting_id, item_id,))
    result = attendance_cursor.rowcount
    print(f"{result} row(s) deleted from additional_attendees")   
    attendance_conn.commit()
    attendance_conn.close()


def initialize_nonselect_attendance_table(conn):
    """Initializes the non-select attendance table."""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nonselect_attendance (
            perNum INTEGER,
            name TEXT,
            designation TEXT,
            meeting_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            attendance_flag TEXT CHECK(attendance_flag in ('Y','N')) ,
            role TEXT CHECK(role in ('HOD', 'Permanent', 'Secretariat', 'ItemOwner', 'AdditionalAttendee', 'DesignateReplacement')),
            remarks TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def load_nonselect_attendance_table():
    """Loads the nonselect attendance table into the database."""
    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_conn.row_factory = sqlite3.Row
    attendance_cursor = attendance_conn.cursor()

    attendance_cursor.execute('PRAGMA table_info(nonselect_attendance)')
    table_checker = attendance_cursor.fetchall()
    if len(table_checker) == 0:
        initialize_nonselect_attendance_table(attendance_conn)
    attendance_conn.close() 


def default_nonselect_attendance_for_meetingid(meeting_id, item_id_list):
    """ Populating the default non-select attendance for meeting_id and all item_ids with 'Y'"""
    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    attendance_cursor = attendance_conn.cursor()
    for item_id in item_id_list:
        coremembers_query = f"INSERT INTO nonselect_attendance SELECT perNum, name, designation, {meeting_id}, {item_id},'Y', role, '' from coremembers;"
        attendance_cursor.execute(coremembers_query)
        secretariat_query = f"INSERT INTO nonselect_attendance SELECT perNum, name, designation, {meeting_id}, {item_id},'Y', 'Secretariat', '' from secretariat;"
        attendance_cursor.execute(secretariat_query)
    item_owner_query = f"INSERT INTO nonselect_attendance SELECT perNum, name, designation, meeting_id, item_id, 'Y', 'ItemOwner', '' from item_owners where meeting_id == ?;"
    attendance_cursor.execute(item_owner_query, (meeting_id,))
    additional_attendees_query = f"INSERT INTO nonselect_attendance SELECT perNum, name, designation, meeting_id, item_id, 'Y', 'AdditionalAttendee', '' from additional_attendees where meeting_id == ?;"
    attendance_cursor.execute(additional_attendees_query, (meeting_id,))
    attendance_conn.commit()
    attendance_conn.close()


def fetch_nonselect_attendance_by_meetingid(meeting_id):
    attendance_conn, attendance_db_was_just_created = connect_attendance_db()
    conn.row_factory = sqlite3.rowcount
    attendance_cursor = attendance_conn.cursor()
    query = "SELECT DISTINCT perNum, name, designation, meeting_id, GROUP_CONCAT(item_id), GROUP_CONCAT(attendance_flag), role, GROUP_CONCAT(remarks) FROM nonselect_attendance WHERE meeting_id = ? GROUP BY perNum"
    rows = attendance_cursor.fetchall()

    try:
        attendance_cursor.execute(query, (meeting_id,))
        rows = attendance_cursor.fetchall()
        data = [dict(row) for row in rows]
    except:
        return None
    
    attendance_conn.close()
    return data
