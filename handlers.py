
from utility import *
from database import User, Award


def error(update: Update, context: CallbackContext):
    """Handling errors raised during handling updates"""
    context.bot.send_message(
        chat_id=settings.DEVELOPER_CHAT_ID, text=format_error_message(update, context), parse_mode='HTML')


def start_private(update: Update, context: CallbackContext):
    buttons = [KeyboardButton(text=loc.get('name')) for loc in settings.LOCALIZATION]
    buttons.append(KeyboardButton(text='Cancel'))

    update.effective_chat.send_message(
        text='Hi! Please, choose a language.',
        reply_markup=ReplyKeyboardMarkup.from_column(
            resize_keyboard=True,
            button_column=buttons
        )
    )

    return settings.CONVERSATION_CHOOSE_LANGUAGE


def choose_language(update: Update, context: CallbackContext):

    loc = get_loc_by_name(update.effective_message.text)

    User.update_or_create(
        user_id=update.effective_user.id,
        bot_chat_id=update.effective_chat.id,
        language=loc.get('shortcut')
    )

    update.effective_chat.send_message(text=loc.get('start_text'), reply_markup=ReplyKeyboardRemove())
    return -1


def wallet(update: Update, context: CallbackContext):

    chat = update.effective_chat

    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        chat.send_text(text='I couldn\'t recognize you. Please, send /start.')
        return -1

    chat.send_text(text=get_loc(user.language).get('wallet_text'))
    return settings.CONVERSATION_PROVIDE_WALLET


def provide_wallet(update: Update, context: CallbackContext):

    wallet = update.effective_message.text
    user = User.update_or_create(
        user_id=update.effective_user.id,
        wallet=wallet
    )

    update.effective_chat.send_text(text=get_loc(user.language).get('wallet_success').format(wallet=wallet))
    return -1


def cancel(update: Update, context: CallbackContext):
    return -1


def new_chat_members(update: Update, context: CallbackContext):
    """Handling new_chat_members messages"""

    if context.bot.id in [user.id for user in update.effective_message.new_chat_members]:
        if group_has_admin(bot=context.bot, chat_id=update.effective_chat.id) is False:
            update.effective_chat.leave()
