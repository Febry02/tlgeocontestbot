
from utility import *
from database import User, Award


def error(update: Update, context: CallbackContext):
    """Handling errors raised during handling updates"""
    context.bot.send_message(
        chat_id=settings.DEVELOPER_CHAT_ID, text=format_error_message(update, context), parse_mode='HTML')


def start(update: Update, context: CallbackContext):
    update.effective_chat.send_message(
        text='Hi! Please, choose a language.',
        reply_markup=ReplyKeyboardMarkup.from_column(
            resize_keyboard=True,
            button_column=[KeyboardButton(text=loc.get('name')) for loc in settings.LOCALIZATION]
        )
    )

    return settings.CONVERSATION_CHOOSE_LANGUAGE


def choose_language(update: Update, context: CallbackContext):

    loc = get_loc_by_name(update.effective_message.text)
    if loc is None:
        log.info('Failed to fetch localization: {}'.format(update.effective_message.text))
        return -1

    user = User.create_or_get(
        user_id=update.effective_user.id,
        bot_chat_id=update.effective_chat.id
    )

    user.update_language(loc.get('shortcut'))
    update.effective_chat.send_message(
        text=loc.get('start_text'), reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return -1


def wallet(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(text='I couldn\'t recognize you. Please, send /start.')
        return -1

    update.effective_chat.send_message(text=get_loc(user.language).get('wallet_text'), parse_mode='HTML')
    return settings.CONVERSATION_PROVIDE_WALLET


def provide_wallet(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(text='I couldn\'t recognize you. Please, send /start.')
        return -1

    wallet = update.effective_message.text
    user.update_wallet(wallet)

    update.effective_chat.send_message(
        text=get_loc(user.language).get('wallet_success_text').format(wallet=wallet), parse_mode='HTML')
    return -1


def balance(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(text='I couldn\'t recognize you. Please, send /start.')
        return -1

    wallet = user.wallet
    if wallet is None:
        update.effective_chat.send_message(
            text=get_loc(user.language).get('wallet_not_provided_text'), parse_mode='HTML')
        return -1

    awards = user.retrieve_awards()
    if awards is None:
        update.effective_chat.send_message(
            text=get_loc(user.language).get('balance_empty_text'), parse_mode='HTML')
        return -1

    update.effective_chat.send_message(
        text=format_user_balance(awards, wallet, get_loc(user.language)), parse_mode='HTML')

def tip(update: Update, context: CallbackContext):
    username = context.match.groupdict().get('username', None)
    geocash = context.match.groupdict().get('geocash', None)
    description = context.match.groupdict().get('description', None)

    log.info(update.effective_chat.get_member(username))


def cancel(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        loc = get_loc('en')
    else:
        loc = get_loc(user.language)

    chat.send_message(text=loc.get('error_text'), reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return -1


def new_chat_members(update: Update, context: CallbackContext):
    """Handling new_chat_members messages"""

    if context.bot.id in [user.id for user in update.effective_message.new_chat_members]:
        if group_has_admin(bot=context.bot, chat_id=update.effective_chat.id) is False:
            update.effective_chat.leave()
