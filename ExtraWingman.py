import discord

import asyncio
import os

import time
import random


class ExtraWingman(discord.Client):
    loop = asyncio.get_event_loop()

    prefix = "TripleFury"
    ready = False
    active = False
    is_available = True

    timer_time = None
    latest_message = None

    def __init__(self, number):
        self.prefix += str(number) + ": "

        self.loop.create_task(self.start(os.getenv("token" + str(number - 1)), bot=False))

        super().__init__()
        print(self.prefix + "Initializing...")

    async def on_ready(self):
        self.ready = True

        await self.change_presence(activity=discord.Game("❤️"))
        print(self.prefix + "Logged in as " + self.user.name + " (" + str(self.user.id) + ")")

    async def on_message(self, message):
        if message.content == "$wingman $w" or message.content == "$wingman $h" or message.content == "$wingman $m":
            self.latest_message = message

    async def roll(self, command):
        self.active = True

        author = self.latest_message.author.name
        message = self.latest_message

        print(self.prefix + "Attempting to roll for " + author)

        #await message.channel.send("Have no fear **" + author + "**, The Waifu Wingman is here to grant you more rolls!")

        time.sleep(1)
        success = False

        while True:
            limited = "**" + self.user.name + "**, the roulette is limited"

            if limited in message.content:
                self.is_available = False
                if not success:
                    author = "Unknown"
                    # reply = "Looks like you didn't actually get any rolls. Calling for backup..."

                await self.change_presence(status=discord.Status.dnd, activity=discord.Game("💔 by " + author))
                self.loop.create_task(self.set_timer(message))
                break

            else:
                await message.channel.send(command)
                try:
                    message = await self.wait_for("message", timeout=5)
                except asyncio.TimeoutError:
                    print(self.prefix + "Timed out, sending another roll...")
                    await message.channel.send(command)

                time.sleep(random.randint(1, 2))

                if message.embeds:
                    success = True

        if success:
            print(self.prefix + "Successfully rolled for " + author)

            reply = "Successfully rolled for **" + author + "**!"
            available_wingmen = 0

            from MainWingman import MainWingman
            for extra_wingman in MainWingman.extra_wingmen:
                if extra_wingman.is_available:
                    available_wingmen += 1
            if available_wingmen > 0:
                reply += " There are **" + str(available_wingmen) + "** more wingmen available. If you would like me to continue rolling, please react to this message!"
            else:
                reply += " There are no more wingmen available 💔. Please try again in later."
            message = await message.channel.send(reply)

            if available_wingmen > 0:
                def check(reaction, user):
                    return str(reaction.emoji) == "💖" and reaction.message.content == message.content and user.name == author

                try:
                    await message.add_reaction("💖")
                    reaction, user = await self.wait_for('reaction_add', timeout=15, check=check)
                    if check(reaction, user): # Reaction Success
                        return False
                except asyncio.TimeoutError:
                    print(self.prefix + "Reaction timed out")


        self.active = False
        return success

    async def set_timer(self, message):
        index = message.content.find("min left")
        minutes = int(''.join(filter(str.isdigit, message.content[index - 5:index])))
        seconds = time.strftime("%S", time.localtime())

        print(self.prefix + "Unavailable for " + str(minutes) + " minutes")

        await asyncio.sleep(minutes * 60 - int(seconds))
        print(self.prefix + "Now Available")
        self.is_available = True
        await self.change_presence(status=discord.Status.online, activity=discord.Game("❤️"))
