#!/usr/bin/env python3
import random
import json

import carbonium_fb

# Here the configuration is stored in a JSON file.
# Create it by copying the login.json.example file and filling it in.
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

# Register another provided command
bot.register(carbonium.contrib.WhereAmICommand(command='where'))
# This command will be called as '%where', according to the setting.

# Create a custom command without subclassing
@bot.register
@carbonium.handlers.CommandHandler.create('coinflip')
def my_command(
        message: carbonium.dataclasses.Message,
        bot_object: carbonium.Bot
    ):
    result = random.choice(['Heads!', 'Tails!'])
    message.reply(result)

# Test out the exception handler
@bot.register
@carbonium.handlers.CommandHandler.create('oops')
def bad_command(message, bot_object):
    raise Exception("This exception will be caught, and a traceback will be DMed to you.")

# Register new handlers during runtime
@bot.register
@carbonium.handlers.CommandHandler.create('selfdestruct')
def selfdestruct_command(
        message: carbonium.dataclasses.Message,
        bot_object
    ):
    mid = message.reply('This message will self-destruct in 15 seconds.')
    bot.register(carbonium.contrib.SelfDestructMessage(mid, 15))


# Start the login routine.
bot.login()
# Start listening for commands and events.
bot.listen()
# This will block while the bot is running.

# You can now go into the conversation with the account you used for the bot
# and send it any of the commands we just defined. Note the prefix!
