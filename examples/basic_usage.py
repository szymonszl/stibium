#!/usr/bin/env python3
import random
import json
import asyncio

import stibium

# Here the configuration is stored in a JSON file.
# Create it by copying the login.json.example file and filling it in.
with open('login.json') as fd:
    config = json.load(fd)

async def main(loop):
    # Create the bot's object
    bot = stibium.Bot(
        loop = loop,
        name = 'Example bot',
        prefix = '%', # Prefix for commands
        owner = config['owner'], # User ID notified about exceptions
        fb_login = ( # A tuple
            config['login'],
            config['password'],
            'cookies.pickle' # Must be a valid and writable path
        )
    )

    # Register a provided command
    # FIXME bot.register(stibium.contrib.EchoCommand())
    # It will use the default 'echo' name, and will be called as '%echo'

    # Register another provided command
    # FIXME bot.register(stibium.contrib.WhereAmICommand(command='where'))
    # This command will be called as '%where', according to the setting.

    # Create a custom command without subclassing
    @bot.register
    @stibium.handlers.CommandHandler.create('coinflip')
    async def my_command(
            message: stibium.dataclasses.Message,
            bot_object: stibium.Bot
        ):
        result = random.choice(['Heads!', 'Tails!'])
        await message.reply(result)

    # Test out the exception handler
    @bot.register
    @stibium.handlers.CommandHandler.create('oops')
    async def bad_command(message, bot_object):
        raise Exception("This exception will be caught, and a traceback will be DMed to you.")

    # Register new handlers during runtime
    '''
    @bot.register
    @stibium.handlers.CommandHandler.create('selfdestruct')
    def selfdestruct_command(
            message: stibium.dataclasses.Message,
            bot_object
        ):
        mid = message.reply('This message will self-destruct in 15 seconds.')
        bot.register(stibium.contrib.SelfDestructMessage(mid, 15)) # FIXME
    '''


    # Start the login routine.
    await bot.login()
    # Start listening for commands and events.
    bot.listen()
    # This will block while the bot is running.

    # You can now go into the conversation with the account you used for the bot
    # and send it any of the commands we just defined. Note the prefix!

loop = asyncio.get_event_loop()
loop.set_debug(True)
loop.run_until_complete(main(loop))
loop.run_forever()
