from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          MessageHandler,
                          CommandHandler,
                          ContextTypes,
                          ConversationHandler,
                          filters)
from dotenv import load_dotenv
from os import getenv

from db import initialization_db, add_note, get_notes, reset_db
from loger import loger_init
from state_constant import ADD_NOTE

# Инициализация логгера
logger = loger_init()


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
        db_msg = "Failed to initialize the database. Please try again later"

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

Please remember: Do not store sensitive information (e.g., passwords, private data) in this bot's database
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


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entering note state")
    await update.message.reply_text(
        "Please send the text of the note or type /cancel to reverse the action"
    )
    return ADD_NOTE


async def recieve_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Wait for user note")

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


async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} invoked the /reset command")

    result = await reset_db(user_id=user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result
    )

    logger.info(f"Reset command successfully processed for User {user_id}")


async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        print("Token is not found!")
        exit()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)

    add_note_handler = ConversationHandler(
        entry_points=[CommandHandler("add_note", note)],
        states={
            ADD_NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recieve_note),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    update_handler = CommandHandler("update", update)
    delete_handler = CommandHandler("delete_note", delete)
    reset_handler = CommandHandler("reset", reset)
    notes_hadler = CommandHandler("notes", notes)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handlers(
        (
            start_handler,
            help_handler,
            add_note_handler,
            update_handler,
            delete_handler,
            reset_handler,
            notes_hadler,
            message_handler,
            unknown_handler,
        )
    )

    application.run_polling()
