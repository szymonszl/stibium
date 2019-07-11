#!/usr/bin/env python3
import random
import json

import carbonium

# Here the configuration is stored in a JSON file.
with open('login.json') as fd:
    config = json.load(fd)

# Create the bot's object
bot = carbonium.Bot(
    name = 'Example bot',
    prefix = '%', # Prefix for commands
    owner = config['owner'], # User ID notified about exceptions
    fb_login = ( # A tuple
        config['login'],
        config['password'],
        'cookies.json' # Must be a valid, writable file.
    )
)

# Register a provided command
bot.register(carbonium.contrib.EchoCommand())
# It will use the default 'echo' name, and will be called as '%echo'

# Create a custom command without subclassing
def my_command(
        message: carbonium.dataclasses.Message,
        bot_object: carbonium.Bot
    ):
    result = random.choice(['Heads!', 'Tails!'])
    message.reply(result)

bot.register(carbonium.handlers.CommandHandler(my_command, 'coinflip'))

# Test out the exception handler
def bad_command(message, bot_object):
    raise Exception("It's your fault.")

bot.register(carbonium.handlers.CommandHandler(bad_command, 'oops'))

# Register new handlers during runtime
def selfdestruct_command(
        message: carbonium.dataclasses.Message,
        bot_object
    ):
    mid = message.reply('This message will self-destruct in 15 seconds.')
    bot.register(carbonium.handlers.SelfDestructMessage(mid, 15))
bot.register(carbonium.handlers.CommandHandler(selfdestruct_command, 'selfdestruct'))


# Start the login routine.
bot.login()
# Start listening for commands and events.
bot.listen()
# This will block while the bot is running.

# You can now go into the conversation with the account you used for the bot
# and send it any of the commands we just defined. Note the prefix!
