from os import environ
import logging
from logging.handlers import RotatingFileHandler
import re
API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
id_pattern = re.compile(r'^.\d+$')
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5965340120 6126812037').split()]

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "Cluster0")
BOT_USERNAME = environ.get('BOT_USERNAME', '')

# If this is True Then Bot Accept New Join Request 
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
JOINLINK = environ.get('JOINLINK', 'https://t.me/+V4qgIH1P7iszZDhl')
LOG_FILE_NAME = "lazydeveloper.txt"

# ========================================================
ACCEPTED_TEXT = "Hey {user}\n\nYour Request For {chat} Is Accepted ✅\nSend /start to Get more Updates.\n\nJoin👇👇\n{joinlink}"
START_TEXT = "Hey {}\n\nI am Auto Request Accept Bot With Working For All Channel. Add Me In Your Channel To Use"

LOG_TEXT = """<b>#👤NewUser
Nᴀᴍᴇ - {}</b>
ID - <code>{}</code>
"""

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)


logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
 