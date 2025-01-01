from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, filters
from .state_constant import ADD_NOTE, DELETE_NOTE, UPDATE_NOTE_ID, UPDATE_NOTE_TEXT


def get_handlers():
    from bot import (
        start, help, enter_add_note, recieve_note,
        enter_update_note_id, recieve_update_note_id, recieve_update_note_text,
        enter_delete_note_id, recieve_delete_note,
        reset, note_list, message, unknown, cancel
    )

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
    list_handler = CommandHandler("list", note_list)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    return [
            start_handler,
            help_handler,
            add_note_handler,
            update_note_handler,
            delete_note_handler,
            reset_handler,
            list_handler,
            message_handler,
            unknown_handler,
        ]
