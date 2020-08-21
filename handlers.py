from urllib.response import addbase

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
        bot_chat_id=update.effective_chat.id,
        username=update.effective_user.username,
        full_name=update.effective_user.full_name
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


@administrators_only
def tip(update: Update, context: CallbackContext):

    if context.match is None:
        update.effective_chat.send_message(
            text=(
                'Wrong syntax. Use: <code>\/tip [@username or fullname] [geocash] [description]</code>\n\n'
                'Example:\n'
                '<pre>\/tip @saulgdmn 5 bonus\n\/tip denis 10 text</pre>'
            ),
            parse_mode='HTML'
        )
        return -1

    username = context.match.groupdict().get('username', None)
    geocash = context.match.groupdict().get('geocash', None)
    description = context.match.groupdict().get('description', None)

    if username is None or geocash is None:
        update.effective_chat.send_message(
            text=(
                'Wrong syntax. Use: <code>\/tip [@username or fullname] [geocash] [description]</code>\n\n'
                'Example:\n'
                '<pre>\/tip @saulgdmn 5 bonus\n\/tip denis 10 text</pre>'
            ),
            parse_mode='HTML'
        )
        return -1

    user = User.search_by_username(username) or User.search_by_name(username)
    if user is None:
        update.effective_chat.send_message('Sorry, user is not founded. Try again.')

    context.user_data['award'] = {
        'user_id': user.user_id,
        'geocash': geocash,
        'description': description,
    }

    update.effective_chat.send_message(
        text='Are you sure to send {} GeoCash to {}?'.format(
            geocash,
            '<a href="tg://user?id={}">{}</a>'.format(
                user.user_id, user.username or user.full_name
            )
        ),
        reply_markup=ReplyKeyboardMarkup.from_column(
            button_column=[KeyboardButton('Yes'), KeyboardButton('No')],
            resize_keyboard=True
        ),
        parse_mode='HTML'
    )

    return settings.CONVERSATION_TIP_CONFIRM


def tip_confirm(update: Update, context: CallbackContext):
    user_id = context.user_data['award'].get('user_id', None)
    geocash = context.user_data['award'].get('geocash', None)
    description = context.user_data['award'].get('description', None)

    if update.message.text == 'No':
        update.effective_chat.send_message(text='Declined.', reply_markup=ReplyKeyboardRemove())
        return -1

    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        update.effective_chat.send_message(text='Something has gone wrong.',  reply_markup=ReplyKeyboardRemove())
        return -1

    user.send_award(geocash=geocash, description=description)
    update.effective_chat.send_message(
        text='User {} received a {} GeoCash award successfully.'.format(
            '<a href="tg://user?id={}">{}</a>'.format(
                user.user_id, user.username or user.full_name
            ),
            geocash
        ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )

    return -1


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
