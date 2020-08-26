import re

from utility import *
from database import User, Award
import eth


def error(update: Update, context: CallbackContext):
    """Handling errors raised during handling updates"""
    context.bot.send_message(
        chat_id=settings.DEVELOPER_CHAT_ID, text=format_error_message(update, context), parse_mode='HTML')


@administrators_only
def load_awards(update: Update, context: CallbackContext):
    file = update.effective_message.document.get_file()
    json_data = json.loads(file.download_as_bytearray())
    log.info(json_data)
    log.info(json_data[0])

    for row in json_data:
        log.info(row)
        user = User.create_or_get(
            user_id=row.get('user_id'),
            username=row.get('username'),
            full_name=row.get('full_name'),
        )

        award = user.create_award(geocash=row.get('geocash'), description='Invite Contest')


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
        loc = get_loc('en')

    user = User.create_or_get(
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        full_name=update.effective_user.full_name,
    )

    user.update_bot_chat_id(update.effective_chat.id)
    user.update_language(loc.get('shortcut'))
    update.effective_chat.send_message(
        text=loc.get('start_text'), reply_markup=ReplyKeyboardRemove(), parse_mode='HTML'
    )
    return -1


def wallet(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(
            text=get_loc('en').get('could_not_recognize_text'), parse_mode='HTML'
        )
        return -1

    update.effective_chat.send_message(text=get_loc(user.language).get('wallet_text'), parse_mode='HTML')
    return settings.CONVERSATION_PROVIDE_WALLET


def provide_wallet(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    user.update_wallet(update.effective_message.text)

    update.effective_chat.send_message(
        text=get_loc(user.language).get('wallet_success_text').format(wallet=user.wallet), parse_mode='HTML'
    )
    return -1


def balance(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(
            text=get_loc('en').get('could_not_recognize_text'), parse_mode='HTML'
        )
        return -1

    awards = user.retrieve_awards()
    if awards is None:
        update.effective_chat.send_message(
            text=get_loc(user.language).get('balance_empty_text'), parse_mode='HTML')
        return -1

    update.effective_chat.send_message(
        text=format_user_balance(awards, wallet, get_loc(user.language)), parse_mode='HTML')


def withdraw(update: Update, context: CallbackContext):
    user = User.get_or_none(User.user_id == update.effective_user.id)
    if user is None:
        update.effective_chat.send_message(
            text=get_loc('en').get('could_not_recognize_text'), parse_mode='HTML'
        )
        return -1

    geocash = user.get_geocash()
    if geocash is None:
        update.effective_chat.send_message(
            text=get_loc(user.language).get('balance_empty_text'), parse_mode='HTML')
        return -1

    wallet = user.wallet
    if wallet is None:
        update.effective_chat.send_message(
            text=get_loc(user.language).get('wallet_not_provided_text'), parse_mode='HTML')
        return -1

    update.effective_chat.send_message(
        text=get_loc(user.language).get('withdraw_text').format(
            geocash=geocash,
            wallet=user.wallet
        ),
        reply_markup=ReplyKeyboardMarkup.from_column(
            button_column=[KeyboardButton('Yes'), KeyboardButton('No')],
            resize_keyboard=True
        ),
        parse_mode='HTML'
    )

    return settings.CONVERSATION_WITHDRAW_CONFIRM


def withdraw_confirm(update: Update, context: CallbackContext):
    if update.message.text != 'Yes':
        update.effective_chat.send_message(text='Declined.', reply_markup=ReplyKeyboardRemove())
        return -1

    user = User.get_or_none(User.user_id == update.effective_user.id)
    geocash = user.get_geocash()
    wallet = user.wallet

    result = eth.make_transaction(
        to=wallet, value=geocash
    )
    if isinstance(result, Exception):
        update.effective_chat.send_message(
            text=get_loc(user.language).get('withdraw_failed_text'),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        raise result

    user.drop_awards()

    update.effective_chat.send_message(
        text=get_loc(user.language).get('withdraw_success_text').format(hash=result),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )
    return -1


@administrators_only
def tip_private(update: Update, context: CallbackContext):
    m = re.match(settings.TIP_PRIVATE_PATT, update.effective_message.text)

    if m is None:
        update.effective_chat.send_message(
            text=(
                'Wrong syntax. Use: <code>/tip [@username or fullname] [geocash] [description]</code>\n\n'
                'Example:\n'
                '<pre>/tip @saulgdmn 5 bonus\n/tip denis 10 text</pre>'
            ),
            parse_mode='HTML'
        )
        return -1

    username = m.groupdict().get('username', None)
    geocash = m.groupdict().get('geocash', None)
    description = m.groupdict().get('description', None)

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


@administrators_only
def tip_group(update: Update, context: CallbackContext):

    if update.effective_message.reply_to_message is None:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                'Wrong syntax. Reply to a user\'s message with: <code>/tip [geocash] [description]</code>\n\n'
                'Example:\n'
                '<pre>/tip 5 bonus</pre>'
            ),
            parse_mode='HTML'
        )
        update.effective_message.delete()
        return -1

    from_user = update.effective_message.reply_to_message.from_user
    m = re.match(settings.TIP_GROUP_PATT, update.effective_message.text)

    if m is None:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                'Wrong syntax. Reply to a user\'s message with: <code>/tip [geocash] [description]</code>\n\n'
                'Example:\n'
                '<pre>/tip 5 bonus</pre>'
            ),
            parse_mode='HTML'
        )
        update.effective_message.delete()
        return -1

    geocash = m.groupdict().get('geocash', None)
    description = m.groupdict().get('description', None)

    user = User.create_or_get(
        user_id=from_user.id,
        username=from_user.username,
        full_name=from_user.full_name,
    )

    user.create_award(geocash=geocash, description=description)

    update.effective_chat.send_message(
        text='Congrats! User {} received a <b>{} GeoCash</b> award!'.format(
            '<a href="tg://user?id={}">{}</a>'.format(
                user.user_id, user.username or user.full_name
            ),
            geocash
        ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )

    if user.bot_chat_id is not None:
        context.bot.send_message(
            chat_id=user.bot_chat_id,
            text=get_loc(user.language).get('award_received_text').format(
                geocash=geocash,
                description=description,
            ),
            parse_mode='HTML'
        )

    update.effective_message.delete()
    return -1


def tip_confirm(update: Update, context: CallbackContext):
    user_id = context.user_data['award'].get('user_id', None)
    geocash = context.user_data['award'].get('geocash', None)
    description = context.user_data['award'].get('description', None)

    if update.message.text != 'Yes':
        update.effective_chat.send_message(text='Declined.', reply_markup=ReplyKeyboardRemove())
        return -1

    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        update.effective_chat.send_message(text='Something has gone wrong.',  reply_markup=ReplyKeyboardRemove())
        return -1

    user.create_award(geocash=geocash, description=description)
    update.effective_chat.send_message(
        text='User {} received a <b>{} GeoCash</b> award successfully.'.format(
            '<a href="tg://user?id={}">{}</a>'.format(
                user.user_id, user.username or user.full_name
            ),
            geocash
        ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )

    context.bot.send_message(
        chat_id=user.bot_chat_id,
        text=get_loc(user.language).get('award_received_text').format(
            geocash=geocash, description=description
        ),
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
