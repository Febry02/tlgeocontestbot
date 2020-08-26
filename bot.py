import logging


from telegram.ext import (
    Updater, Dispatcher, Filters, CommandHandler, MessageHandler, ConversationHandler
)

import settings
import handlers
import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def main():
    updater: Updater = Updater(token=settings.BOT_API_TOKEN, use_context=True)
    dp: Dispatcher = updater.dispatcher

    dp.add_error_handler(handlers.error)
    dp.add_handler(MessageHandler(
        filters=Filters.status_update.new_chat_members, callback=handlers.new_chat_members))
    dp.add_handler(MessageHandler(
        filters=Filters.status_update.chat_created, callback=handlers.chat_created_handler))
    dp.add_handler(MessageHandler(
        filters=Filters.document & Filters.forwarded, callback=handlers.load_awards))

    dp.add_handler(CommandHandler(
        filters=~Filters.private, command='tip', callback=handlers.tip_group))
    dp.add_handler(CommandHandler(
        filters=Filters.private, command='balance', callback=handlers.balance))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(filters=Filters.private, command='start', callback=handlers.start)],
        states={
            settings.CONVERSATION_CHOOSE_LANGUAGE: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=handlers.choose_language)
            ],
        },
        fallbacks=[MessageHandler(filters=~Filters.text, callback=handlers.cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(filters=Filters.private, command='tip', callback=handlers.tip_private)],
        states={
            settings.CONVERSATION_TIP_CONFIRM: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=handlers.tip_confirm)
            ]
        },
        fallbacks=[MessageHandler(filters=~Filters.text, callback=handlers.cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(filters=Filters.private, command='withdraw', callback=handlers.withdraw)],
        states={
            settings.CONVERSATION_WITHDRAW_CONFIRM: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=handlers.withdraw_confirm)
            ]
        },
        fallbacks=[MessageHandler(filters=~Filters.text, callback=handlers.cancel)]
    ))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(filters=Filters.private, command='wallet', callback=handlers.wallet)],
        states={
            settings.CONVERSATION_PROVIDE_WALLET: [
                MessageHandler(filters=Filters.regex(settings.WALLET_PATT), callback=handlers.provide_wallet)
            ],
        },
        fallbacks=[MessageHandler(filters=~Filters.regex(settings.WALLET_PATT), callback=handlers.cancel)]
    ))

    if settings.DEBUG_MODE:
        updater.start_polling()
    else:
        updater.start_webhook(
            listen='0.0.0.0',
            port=settings.SERVER_WEBHOOK_PORT,
            url_path=settings.BOT_API_TOKEN,
            key='private.key',
            cert='public.pem',
            webhook_url='https://{}:{}/{}'.format(
                settings.SERVER_WEBHOOK_IP, settings.SERVER_WEBHOOK_PORT, settings.BOT_API_TOKEN))

    updater.idle()


if __name__ == '__main__':
    main()
