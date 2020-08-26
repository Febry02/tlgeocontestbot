import logging
import traceback
import html
import json

from functools import wraps

import yaml
from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
    )
from telegram.ext import CallbackContext

import settings

log = logging.getLogger(__name__)


def load_config(path):
    try:
        with open(path, 'r', encoding='utf8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        log.info('Failed to load {}: {}'.format(path, e))
        return None


def load_localization(path):
    try:
        with open(path, 'r', encoding='utf8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        log.info('Failed to load {}: {}'.format(path, e))
        return None


def load_json(path):
    try:
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log.info('Failed to load {}: {}'.format(path, e))
        return None


def get_loc_by_name(name):
    for loc in settings.LOCALIZATION:
        if loc['name'] == name:
            return loc


def get_loc(shortcut):
    for loc in settings.LOCALIZATION:
        if loc['shortcut'] == shortcut:
            return loc


def administrators_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in settings.ADMINISTRATOR_IDS:
            log.info("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def group_has_admin(bot, chat_id):
    ids = [m.user.id for m in bot.get_chat_administrators(chat_id=chat_id)]
    for admin_id in settings.ADMINISTRATOR_IDS:
        if admin_id in ids:
            return True
    return False


def format_error_message(update: Update, context: CallbackContext):
    text = 'An exception was raised while handling an update:\n'
    if update:
        text += '<pre>update = {}</pre>\n\n'.format(
            html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)))
    if context.bot_data:
        text += '<pre>context.bot_data = {}</pre>\n\n'.format(
            html.escape(json.dumps(context.bot_data, indent=2, ensure_ascii=False)))
    if context.chat_data:
        text += '<pre>context.chat_data = {}</pre>\n\n'.format(
            html.escape(json.dumps(context.chat_data, indent=2, ensure_ascii=False)))
    if context.user_data:
        text += '<pre>context.user_data = {}</pre>\n\n'.format(
            html.escape(json.dumps(context.user_data, indent=2, ensure_ascii=False)))
    if context.job:
        text += '<pre>context.job = {}</pre>\n\n'.format(context.job)
    if context.matches:
        text += '<pre>context.matches = {}</pre>\n\n'.format(context.matches)
    if context.args:
        text += '<pre>context.args = {}</pre>\n\n'.format(context.args)

    tb = ''.join(traceback.format_exception(None, context.error, context.error.__traceback__))
    text += '<pre>{}</pre>'.format(html.escape(tb))
    return text


def format_user_balance(awards, wallet, loc):
    return loc.get('balance_text').format(
        user_awards='\n'.join([
                loc.get('user_award_patt').format(geocash=award.get('geocash'), description=award.get('description'))
                for award in awards
            ]),
        balance=sum([award.get('geocash') for award in awards])
    )
