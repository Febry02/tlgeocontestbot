export $(grep -v '^#' .env | xargs)
./venv/bin/python3 bot.py