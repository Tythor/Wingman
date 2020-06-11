import discord
import aiohttp

import time
import random
import os

# from discord.ext import command

class Wingman(discord.Client):
    def __init__(self):
        self.ready = False
        self.active = False
        super().__init__()
        print("Starting...")

    def run(self):
        token = os.getenv("token")
        super().run(token, bot=False)

    async def roll(self, message, command):
        if not self.active:
            self.active = True
            print("Rolling for " + message.author.name)
            await message.channel.send("Have no fear, The Waifu Wingman is here to grant you more rolls!")

            msg = None
            time.sleep(1)

            while True:
                keyword = self.user.name + ", the roulette is limited"
                if msg is not None and keyword in msg.content:
                    await message.channel.send("It appears that I am out of rolls. Please try again later.")
                    break
                else:
                    await message.channel.send(command)
                    msg = await self.wait_for("message")
                    time.sleep(random.randint(1, 2))
            self.active = False


    # @command()
    # async def wingman(self, message, arg):
    #    print("apsoidjfaposid")
    #    self.roll(message, arg)

    async def on_message(self, message):
        if message.content == "$wingman $w":
            await self.roll(message, "$w")
        elif message.content == "$wingman $h":
            await self.roll(message, "$h")
        elif message.content == "$wingman $m":
            await self.roll(message, "$m")

        if not self.ready:
            return
        """"
        # SelfBot Commands
        prefix_checks = [
            message.content.startswith(self.prefix),
            message.author.id == self.user.id
        ]
        if all(prefix_checks):
            def arg_check(arg):
                str_mentions = [str(mention) for mention in raw_mentions]
                if not raw_mentions:
                    return True
                checks = [
                    raw_mentions,
                    arg != '',
                    arg.replace('<@', '').replace('>', '') not in str_mentions
                ]
                return all(checks)

            raw_mentions = message.raw_mentions or None
            detokenized = message.content.split(' ')
            cmd = detokenized[0]
            args = []
            if len(detokenized) > 1:
                if raw_mentions:
                    args = [
                        arg for arg in detokenized[1:] if arg_check(arg)
                    ]
                else:
                    args = [arg for arg in detokenized[1:] if arg != '']
            cmd = cmd.replace(self.prefix, 'cmd_').lower()
            try:
                method = self.__getattribute__(cmd)
            except AttributeError:  # Not a selfbot command, so execute it as a PokeCord command.
                cmd = cmd.replace('cmd_', '')
                args.insert(0, cmd)
                method = self.cmd_poke_exec
            kwargs = {
                'message': message,
                'args': args,
                'mentions': []
            }
            if message.mentions:
                kwargs['mentions'] = message.mentions
            required = inspect.signature(method)
            required = set(required.parameters.copy())
            for key in list(kwargs):
                if key not in required:
                    kwargs.pop(key, None)
            if required == set(kwargs):
                await method(**kwargs)
        """

    async def cmd_autolog(self, message, args=[]):
        if args:
            if args[0].lower() == 'off':
                self.autolog = False
                print('Disabled Autologger.\n')
            elif args[0].lower() == 'on':
                self.autolog = True
                print('Enabled Autologger.\n')
            else:
                print(args)

    async def on_ready(self):
        self.sess = aiohttp.ClientSession(loop=self.loop)
        self.ready = True
        await self.change_presence(status=discord.Status.online, activity=discord.Game("$wingman $w | $h | $m"))
        print("Logged in as " + self.user.name + " (" + str(self.user.id) + ")")
