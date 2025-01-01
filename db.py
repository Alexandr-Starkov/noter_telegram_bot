import sqlite3
import os
import datetime
import textwrap
from typing import Any


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
                                params: tuple = ()) -> str | list[Any]:
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


async def update_note(user_id: str, note_id: str, new_note_text: str) -> str:
    from bot import logger

    query = "UPDATE Notes SET Note = (?) WHERE ID = (?)"
    params = (new_note_text, note_id)

    try:
        await execute_db_operations(
            user_id=user_id, sql_query=query, params=params
        )
        return "Note successfully update"
    except RuntimeError as e:
        logger.error("Error while updating note for user {user_id}: {str(e)}")
        return f"An error occurred while updating note: {str(e)}"


async def delete_note(user_id: str, note: str) -> str:
    from bot import logger

    delete_query = "DELETE FROM Notes WHERE ID = (?)"
    params = (note.strip(),)

    try:
        result = await execute_db_operations(
            user_id, sql_query=delete_query, params=params
        )
    except RuntimeError as e:
        logger.error((f"Error while delete note for user {user_id}: {str(e)}"))
        return f"An error occurred while deleting note: {str(e)}"

    return result


async def reset_db(user_id: str) -> str:
    from bot import logger

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
        logger.error(f"Error reseting database for user {user_id}: {str(e)}")
        return f"An error occurred while reset database: {str(e)}"


async def get_notes(user_id: str, raw: bool = None) -> str:
    from bot import logger

    query = "SELECT * FROM Notes"

    try:
        result = await execute_db_operations(
            user_id=user_id, sql_query=query
        )
        if not result:
            return "You don't have any notes yet."

    except RuntimeError as e:
        logger.error(f"Error fetching notes for user {user_id}: {str(e)}")
        return f"An error occurred while fetching notes: {str(e)}"

    if raw:
        return [raw for raw in result]
    else:
        note_list = await to_format_note_list(result)
        return note_list


async def to_format_note_list(result) -> str:
    note_width = 40
    formatted_notes = []

    for row in result:
        wrapped_note = textwrap.fill(row[1], note_width)
        formatted_notes.append(f"{row[0]}. {wrapped_note} - {row[2]}")

    return "\n".join(formatted_notes)
