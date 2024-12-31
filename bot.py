from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          MessageHandler,
                          CommandHandler,
                          ContextTypes,
                          ConversationHandler,
                          filters)
from dotenv import load_dotenv
from os import getenv

from db import initialization_db, add_note, get_notes, reset_db, delete_note, update_note
from logger import logger_init
from state_constant import ADD_NOTE, DELETE_NOTE, UPDATE_NOTE_ID, UPDATE_NOTE_TEXT

# Инициализация логгера
logger = logger_init()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started bot")

    welcome_msg = """
Welcome to the Noter!
Your database will be created automatically, the bot can only use one database per user.
Use /help to see available commands.

Please note: This bot is not designed to store sensitive information, such as passwords or personal data.
"""
    await context.bot.send_message(
        chat_id=user_id,
        text=welcome_msg
    )

    try:
        db_msg = await initialization_db(user_id)
        logger.info(f"Database initialized successfully for User {user_id}")
    except RuntimeError as e:
        logger.error(f"Error initializing db for User {user_id}: {e}")
        db_msg = "Failed to initialize the database. Please try again later."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=db_msg
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} invoked the /help command")

    command_list = """
Bot accepts the following commands:
/start - To initialize the database
/help - All available commands
/add_note - To add note to database
/update - To update note in database
/delete - To delete note in database
/notes - To get a list of notes
/reset - To clear database

Please remember: Do not store sensitive information (e.g., passwords, private data) in this bot's database.
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=command_list
    )

    logger.info(f"Help command successfully processed for User {user_id}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Needs to terminate the process and exits the bot from the current state"""
    logger.info("Canceling the process")

    await update.message.reply_text("Operation cancelled. You can use another command.")
    return ConversationHandler.END


async def enter_add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering note state")
    await update.message.reply_text(
        "Please send the text of the note or type /cancel to reverse the action."
    )
    return ADD_NOTE


async def recieve_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Wait for user note to add")

    user_note = update.message.text.strip()
    user_id = update.effective_user.id

    if not user_note:
        msg = "Note is empty."
        logger.info(f"User {user_id} send an empty note")
    elif len(user_note) > 350:
        msg = "Note is too large. Note limit is set to 350 characters."
        logger.info(f"User {user_id} send too long note")
    else:
        msg = await add_note(user_id=user_id, note=user_note)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

    logger.info("Note received and processed")
    return ConversationHandler.END


async def enter_update_note_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering update state")

    await update.message.reply_text(
        text="Please send the ID of the note you want to update, or type /cancel to reverse the action."
    )

    return UPDATE_NOTE_ID


async def enter_update_note_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering update-note state")

    await update.message.reply_text(
        text="Please send the new text for the note, or type /cancel to reverse the action."
    )

    return UPDATE_NOTE_TEXT


async def recieve_update_note_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Waiting for user note number for update")
    user_note_number = update.message.text.strip()
    user_id = update.effective_user.id

    try:
        note_id = int(user_note_number)
    except ValueError:
        logger.info("The user entered an invalid ID format")
        msg = "The entered ID is not valid. Please enter a number."
        await update.message.reply_text(msg)
        return ConversationHandler.END

    notes = await get_notes(user_id=user_id, raw=True)
    ids = [str(note[0]) for note in notes]

    if str(note_id) not in ids:
        logger.info(f"User {user_id} entered a non-existent ID: {note_id}")
        msg = "This note ID does not exist."
        await update.message.reply_text(msg)
        return ConversationHandler.END

    context.user_data["note_id"] = note_id
    await recieve_update_note_text(update, context)

    return UPDATE_NOTE_TEXT


async def recieve_update_note_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Waiting user to get new note text")

    note_text = update.message.text.strip()
    user_id = update.effective_user.id
    note_id = context.user_data.get("note_id")

    if not note_text:
        logger.info("The user entered empty note text")
        msg = "The note text cannot be empty."
        await update.message.reply_text(msg)
        return ConversationHandler.END

    result = await update_note(user_id=user_id, note_id=note_id, new_note_text=note_text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result
    )

    return ConversationHandler.END


async def enter_delete_note_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering delete state")

    await update.message.reply_text(
        text="Please send the number of the note or type /cancel to reverse the action."
    )

    return DELETE_NOTE


async def recieve_delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Waiting for user note number for delete")

    user_note_number = update.message.text.strip()
    user_id = update.effective_user.id

    try:
        note_id = int(user_note_number)
    except ValueError:
        logger.info("The user entered an invalid ID format")
        msg = "The entered ID is not valid. Please enter a number."
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg
        )
        return ConversationHandler.END

    notes = await get_notes(user_id, raw=True)
    ids = [str(note[0]) for note in notes]

    if user_note_number not in ids:
        logger.info(f"User {user_id} entered a non-existent ID: {note_id}")
        msg = "This note ID does not exist."
    else:
        msg = await delete_note(user_id=user_id, note=user_note_number)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

    logger.info(
        f"Note deletion processed for user {user_id}, note ID: {note_id}")
    return ConversationHandler.END


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} invoked the /reset command")

    msg = await reset_db(user_id=user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

    logger.info(f"Reset command successfully processed for User {user_id}")


async def note_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} invoked the /notes command")

    note_list = await get_notes(user_id=user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=note_list
    )

    logger.info(f"Notes command successfully processed for User {user_id}")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    logger.info(f"User {user_id} type message: '{user_message}' to bot")

    msg = "This is not a command, use /help"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

    logger.info(
        f"Bot send Not a command message to User {user_id} after receiving: '{user_message}'")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    logger.info(
        f"User {user_id} send unknown command: '{user_message}' to bot")

    msg = "Unknown command, use /help"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )

    logger.info(
        f"Bot send 'Unknown command' to User {user_id} after receiving: '{user_message}'")


if __name__ == "__main__":
    load_dotenv()
    TELEGRAM_TOKEN = getenv("TELEGRAM-TOKEN")

    if not TELEGRAM_TOKEN:
        logger.info("Token is not found!")
        exit()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)

    add_note_handler = ConversationHandler(
        entry_points=[CommandHandler("add_note", enter_add_note)],
        states={
            ADD_NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recieve_note),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    update_note_handler = ConversationHandler(
        entry_points=[CommandHandler("update", enter_update_note_id)],
        states={
            UPDATE_NOTE_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               recieve_update_note_id),
                CommandHandler("cancel", cancel)
            ],
            UPDATE_NOTE_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               recieve_update_note_text),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    delete_note_handler = ConversationHandler(
        entry_points=[CommandHandler("delete", enter_delete_note_id)],
        states={
            DELETE_NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               recieve_delete_note),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    reset_handler = CommandHandler("reset", reset)
    notes_hadler = CommandHandler("notes", note_list)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handlers(
        (
            start_handler,
            help_handler,
            add_note_handler,
            update_note_handler,
            delete_note_handler,
            reset_handler,
            notes_hadler,
            message_handler,
            unknown_handler,
        )
    )

    application.run_polling()
