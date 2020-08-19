import os

from utility import load_config, load_localization

DEBUG_MODE = True if os.getenv('DEBUG_MODE') == 'true' else False

CONFIG = load_config(os.getenv('CONFIG_PATH'))
LOCALIZATION = load_localization(os.getenv('LOCALIZATION_PATH'))

BOT_API_TOKEN = CONFIG.get('BOT_API_TOKEN')
DATABASE_PATH = CONFIG.get('DATABASE_PATH')

ADMINISTRATOR_IDS = [401042341, 544498153]
DEVELOPER_CHAT_ID = 544498153

CONVERSATION_CHOOSE_LANGUAGE = 1
CONVERSATION_PROVIDE_WALLET = 2
