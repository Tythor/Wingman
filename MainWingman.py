import asyncio
import discord

import time
import random
import os

from ExtraWingman import ExtraWingman


class MainWingman(discord.Client):
    loop = asyncio.get_event_loop()

    prefix = "TripleFury2: "
    ready = False
    active = False
    is_available = True

    extra_wingmen = []


    def __init__(self):
        self.loop.create_task(self.start(os.getenv("token"), bot=False))

        super().__init__()
        print(self.prefix + "Initializing...")

        for i in range(4): # up to 4
            self.extra_wingmen.append(ExtraWingman(i + 3))
        self.loop.run_forever()

    async def on_ready(self):
        self.ready = True

        #await self.change_presence(activity=discord.Game("$wingman $w | $h | $m"))
        await self.change_presence(activity=discord.Game("❤️"))

        print(self.prefix + "Logged in as " + self.user.name + " (" + str(self.user.id) + ")")

    async def on_message(self, message):
        if not self.ready or self.active:
            return
        if message.content == "$wingman $w":
            await self.roll(message, "$w")
        elif message.content == "$wingman $h":
            await self.roll(message, "$h")
        elif message.content == "$wingman $m":
            await self.roll(message, "$m")

    async def roll(self, message, command):
        self.active = True

        author = message.author.name
        
        if self.is_available:
            print(self.prefix + "Attempting to roll for " + author)
    
            await message.channel.send("Have no fear **" + author + "**, The Waifu Wingmen are here to grant you more rolls!")
            time.sleep(1)

        success = False

        while True and self.is_available:
            limited = "**" + self.user.name + "**, the roulette is limited"
            disabled = "Command DISABLED"

            if disabled in message.content:
                return

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

            available_wingmen = 0
            for extra_wingman in self.extra_wingmen:
                if extra_wingman.is_available:
                    available_wingmen += 1
            message = await message.channel.send("Successfully rolled for **" + author + "**! There are `" + str(available_wingmen) + "` more wingmen available. If you would like me to continue rolling, please react to this message!")

            def check(reaction, user):
                return str(reaction.emoji) == "💖" and reaction.message.content == message.content and user.name == author

            try:
                await message.add_reaction("💖")
                reaction, user = await self.wait_for('reaction_add', timeout=15, check=check)
                if check(reaction, user): # Reaction Success
                    await self.call_help(message, command)
            except asyncio.TimeoutError:
                print(self.prefix + "Reaction timed out")
        else: # Call for Help
            await self.call_help(message, command)

        self.active = False

    async def call_help(self, message, command):
        helped = False
        for extra_wingman in self.extra_wingmen:
            if extra_wingman.is_available:
                helped = True
                stop_rolling = await extra_wingman.roll(command)
                if stop_rolling:
                    break

        if not helped:
            time.sleep(1)
            await message.channel.send("Sorry, looks like all of the wingmen are unavailable 💔. Please try again later.")

    async def set_timer(self, message):
        index = message.content.find("min left")
        minutes = int(''.join(filter(str.isdigit, message.content[index - 5:index])))
        seconds = time.strftime("%S", time.localtime())

        print(self.prefix + "Unavailable for " + str(minutes) + " minutes")

        await asyncio.sleep(minutes * 60 - int(seconds))
        print(self.prefix + "Now Available")
        self.is_available = True
        await self.change_presence(status=discord.Status.online, activity=discord.Game("❤️"))