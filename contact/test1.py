import subprocess
import logging
import telegram
repo_url = "https://github.com/python-telegram-bot/python-telegram-bot.git"
destination = "my_repo"

subprocess.run(["git", "clone", repo_url, destination], check=True)
print("Cloned successfully")