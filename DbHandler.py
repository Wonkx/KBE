import os
import sqlite3
from sqlite3 import Error
from typing import Literal

def create_connection(db_file: str) -> sqlite3.Connection:
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn: sqlite3.Connection, create_table_sql: Literal) -> None:
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_submission(conn: sqlite3.Connection, submission: list) -> int:
    """
    Create a new submission into the submissions table
    :param conn:
    :param submission:
    :return: submission id
    """
    sql = ''' INSERT INTO submissions(apartmentCount,size,balcony)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, submission)
    conn.commit()
    return cur.lastrowid

def select_all_submissions(conn: sqlite3.Connection) -> None:
    """
    Query all rows in the submissions table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM submissions")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def setup() -> None:
    database_path = os.path.dirname(os.path.abspath(__file__))
    database_path += r"\kb.db"

    inhabitant_submissions_sql_table = """ CREATE TABLE IF NOT EXISTS submissions (
                                        id integer PRIMARY KEY,
                                        apartmentCount integer NOT NULL,
                                        size integer NOT NULL,
                                        balcony integer NOT NULL,
                                        email text NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(database_path)

    if conn is not None:
        create_table(conn, inhabitant_submissions_sql_table)
        select_all_tasks(conn)
    else:
        print("Error! cannot create the database connection.")

