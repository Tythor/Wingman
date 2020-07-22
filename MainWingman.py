import discord

import asyncio
import os

import time
import datetime
import math
import random

from ExtraWingman import ExtraWingman


class MainWingman(discord.Client):
    loop = asyncio.get_event_loop()

    prefix = "TripleFury2: "
    ready = False
    active = False
    is_available = True

    timer_time = None
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
        if not self.ready or self.active or message.author == self.user or not message.content[:8] == "$wingman":
            return

        command = message.content[9:]
        if (command == "$w" or command == "$h" or command == "$m"
                or command == "$wg" or command == "$hg" or command == "$mg"
                or command == "$wa" or command == "$ha" or command == "$ma"):
            await self.roll(message, command)
        elif "$give" in command:
            await self.give(message, message.author, command)
        elif "$del" in command:
            i = 0
            async for msg in message.channel.history():
                if i > int(command[4:]):
                    break
                else:
                    await msg.delete()
                i += 1

    async def on_reaction_add(self, reaction, user):
        if not reaction.message.embeds or "Mudamaid" in user.name:
            return

        if not (reaction.emoji == "❤️" or reaction.emoji == "💖" or reaction.emoji == "💘" or reaction.emoji == "💓" or reaction.emoji == "💗" or reaction.emoji == "💕"):
            return

        for i in range(2, 7):
            if user.name == "TripleFury" + str(i):
                return

        self.loop.create_task(self.claim(reaction, user))

    async def claim(self, reaction, user):
        def check(message):
            return "married" in message.content and user.name in message.content

        def check2(message):
            return "married" in message.content and self.user.name in message.content

        try:
            await self.wait_for("message", timeout=5, check=check)
        except asyncio.TimeoutError: # Claimed Unsuccessfully
            message = reaction.message
            waifu = message.embeds[0].author.name

            print(self.prefix + "Attempting to claim " + waifu + " for " + user.name)

            await message.add_reaction(reaction.emoji)

            try:
                await self.wait_for("message", timeout=5, check=check2)
            except asyncio.TimeoutError:  # Claimed Unsuccessfully
                for extra_wingman in self.extra_wingmen:
                    if await extra_wingman.claim(message, reaction, user):
                        break
            else: # Claimed Successfully
                await message.channel.send("Successfully claimed **" + waifu + "** for **" + user.name + "**! Use $wingman $give <character> to receive your claim!")
                await self.give(message, user, "$give " + waifu)

    async def give(self, message, user, command):
        await asyncio.sleep(1)

        waifu = command[6:]
        msg = await message.channel.send("$give " + user.mention + " " + waifu)

        def check(message):
            return "Who" in message.content

        try:
            msg2 = await self.wait_for("message", timeout=2, check=check)
        except asyncio.TimeoutError: # Successful
            print(self.prefix + "Offered " + waifu + " to " + user.name)
        else: # Unsuccessful
            await message.channel.send("$exit", delete_after=2)

            try:
                await (await self.wait_for("message", timeout=2)).delete()
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(1)
            await msg.delete()
            await msg2.delete()

            for extra_wingman in self.extra_wingmen:
                if await extra_wingman.give(message, user, command):
                    break

    async def roll(self, message, command):
        self.active = True

        og_message = message
        author = message.author.name

        if self.is_available:
            print(self.prefix + "Attempting to roll for " + author)

            await message.channel.send("Have no fear **" + author + "**, The Waifu Wingmen are here to grant you more rolls!")
            await asyncio.sleep(1)

        success = False

        while True and self.is_available:
            limited = "**" + self.user.name + "**, the roulette is limited"
            disabled = "Command DISABLED"
            restricted = "Command RESTRICTED"

            if disabled in message.content or restricted in message.content:
                return

            if limited in message.content:
                self.is_available = False
                if not success:
                    await message.delete()
                    author = "Unknown"
                    # reply = "Looks like you didn't actually get any rolls. Calling for backup..."

                await self.change_presence(status=discord.Status.dnd, activity=discord.Game("💔 by " + author))
                self.loop.create_task(self.set_timer(message))
                break

            else:
                await message.channel.send(command, delete_after=2)
                try:
                    message = await self.wait_for("message", timeout=5)
                except asyncio.TimeoutError:
                    print(self.prefix + "Timed out, sending another roll...")
                    await message.channel.send(command, delete_after=2)

                await asyncio.sleep(random.randint(1, 2))

                if message.embeds:
                    success = True

        self.active = False

        if success:
            print(self.prefix + "Successfully rolled for " + author)

            available_wingmen = 0
            for extra_wingman in self.extra_wingmen:
                if extra_wingman.is_available:
                    available_wingmen += 1
            message = await message.channel.send("Successfully rolled for **" + author + "**! There are **" + str(available_wingmen) + "** more wingmen available. If you would like me to continue rolling, please react to this message!")

            def check(reaction, user):
                return str(reaction.emoji) == "💖" and reaction.message.content == message.content and user.name == author

            try:
                await message.add_reaction("💖")
                await self.wait_for("reaction_add", timeout=15, check=check)
            except asyncio.TimeoutError:
                print(self.prefix + "Reaction timed out")
            else: # Reaction Success
                if not self.active:
                    await self.call_help(og_message, command)

        else: # Call for Help
            await self.call_help(og_message, command)

    async def call_help(self, message, command):
        helped = False
        for extra_wingman in self.extra_wingmen:
            if extra_wingman.is_available:
                if await extra_wingman.roll(message, command):
                    helped = True
                    break

        if not helped:
            await asyncio.sleep(1)
            minutes_left = self.timer_time - datetime.datetime.now()
            await message.channel.send("Sorry, looks like all of the wingmen are unavailable 💔. Please try again in **" + str(math.ceil(minutes_left.seconds / 60)) + "** minutes.")

    async def set_timer(self, message):
        index = message.content.find("min left")
        minutes = int("".join(filter(str.isdigit, message.content[index - 5:index])))
        seconds = time.strftime("%S", time.localtime())

        self.timer_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

        print(self.prefix + "Unavailable for " + str(minutes) + " minutes")

        await asyncio.sleep(minutes * 60 - int(seconds))
        print(self.prefix + "Now Available")
        self.is_available = True
        await self.change_presence(status=discord.Status.online, activity=discord.Game("❤️"))

    # Leaderboard Stuff
    # my_last_message = await message.channel.history().get(author=self.user)
    # print(my_last_message.content)