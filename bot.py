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
    dp.add_handler(MessageHandler(filters=Filters.status_update.new_chat_members, callback=handlers.new_chat_members))
    dp.add_handler(CommandHandler(command='balance', callback=handlers.balance))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler(filters=Filters.private, command='start', callback=handlers.start),
            CommandHandler(filters=Filters.private, command='wallet', callback=handlers.wallet)
        ],
        states={
            settings.CONVERSATION_PROVIDE_WALLET: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=handlers.provide_wallet)
            ],
            settings.CONVERSATION_CHOOSE_LANGUAGE: [
                MessageHandler(filters=Filters.text & ~Filters.command, callback=handlers.choose_language)
            ]
        },
        fallbacks=[
            MessageHandler(filters=~Filters.text, callback=handlers.cancel)
        ]
    ))

    if settings.DEBUG_MODE:
        updater.start_polling()
    else:
        pass
        '''
        updater.start_webhook(
            listen='0.0.0.0',
            port=settings.SERVER_WEBHOOK_PORT,
            url_path=settings.BOT_API_TOKEN,
            key='private.key',
            cert='public.pem',
            webhook_url='https://{}:{}/{}'.format(
                settings.SERVER_WEBHOOK_IP, settings.SERVER_WEBHOOK_PORT, settings.BOT_API_TOKEN))
                '''

    updater.idle()


if __name__ == '__main__':
    main()
