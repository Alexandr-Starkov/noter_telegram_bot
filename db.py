import sqlite3
import os
import datetime
from typing import Any, Optional


async def initialization_db(user_id: str) -> str:
    db_path = f"./db/{user_id}_db.sqlite"
    if os.path.exists(db_path):
        return "Your database already exists! You can start adding notes."
    try:
        os.makedirs('./db', exist_ok=True)

        conn = sqlite3.connect(f"./db/{user_id}_db.sqlite")
        c = conn.cursor()
        c.execute("""
                CREATE TABLE IF NOT EXISTS Notes(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Note TEXT NOT NULL,
                    Date TEXT NOT NULL
                )
                """)

        conn.commit()
        conn.close()

        return "Your database has been initialized successfully!"
    except FileNotFoundError as e:
        raise RuntimeError("Error creating directory") from e
    except PermissionError as e:
        raise RuntimeError("Permission error") from e
    except sqlite3.DatabaseError as e:
        raise RuntimeError("Database error") from e
    except sqlite3.ProgrammingError as e:
        raise RuntimeError("Programming error") from e
    except sqlite3.OperationalError as e:
        raise RuntimeError("Operational error") from e
    except Exception as e:
        raise RuntimeError("Unexpected error") from e


async def execute_db_operations(user_id: str,
                                sql_query: str,
                                params: tuple = ()) -> Optional[Any]:
    db_path = f"./db/{user_id}_db.sqlite"
    result = None

    try:
        if not os.path.exists(db_path):
            raise FileNotFoundError("Database does not exist")

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(sql_query, params)

        if sql_query.strip().lower().startswith("select"):
            result = c.fetchall()
        else:
            result = "Operation success!"

        conn.commit()
        return result
    except FileNotFoundError as e:
        raise RuntimeError("Data base is not exist") from e
    except sqlite3.Error as e:
        raise RuntimeError("Data base error!") from e
    except Exception as e:
        raise RuntimeError("An error occured, try later!") from e
    finally:
        if conn:
            conn.close()


async def add_note(user_id: str, note: str) -> str:
    from bot import logger

    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    query = "INSERT INTO Notes (Note, Date) VALUES (?, ?)"
    params = (note.strip(), current_date)

    try:
        result = await execute_db_operations(
            user_id=user_id, sql_query=query, params=params
        )
    except RuntimeError as e:
        logger.error(f"Error fetching notes for user {user_id}: {str(e)}")
        return f"An error occurred while fetching notes: {str(e)}"

    return result


async def update_note(user_id: str, note: str, new_note: str) -> str:
    pass


async def delete_note(user_id: str, note: str) -> str:
    pass


async def reset_db(user_id: str) -> str:
    delete_query = "DELETE FROM Notes;"
    reset_query = "DELETE FROM sqlite_sequence WHERE name='Notes';"

    try:
        delete_query = await execute_db_operations(
            user_id=user_id, sql_query=delete_query
        )
        reset_query = await execute_db_operations(
            user_id=user_id, sql_query=reset_query
        )

        return "The database has been reset successfully!"
    except RuntimeError as e:
        return f"An error occurred while fetching notes: {str(e)}"


async def get_notes(user_id: str) -> str:
    from bot import logger

    query = "SELECT * FROM Notes"

    try:
        result = await execute_db_operations(
            user_id=user_id, sql_query=query
        )
        if not result:
            return "You don't have any notes yet"

    except RuntimeError as e:
        logger.error(f"Error fetching notes for user {user_id}: {str(e)}")
        return f"An error occurred while fetching notes: {str(e)}"

    note_list = ''
    for i, row in enumerate(result):
        note_list += ' '.join(str(j) for j in row)
        if i < len(result) - 1:
            note_list += '\n'

    return note_list
