import discord
import asyncio
import datetime
import math

from wingman import Wingman


class MainWingman(Wingman):
    timer_time = None
    is_active = {}
    extra_wingmen = []

    def __init__(self, extra_wingmen):
        super().__init__(1)
        MainWingman.extra_wingmen = extra_wingmen

    async def on_message(self, message):
        if message.author == self.user or not message.content.startswith("$wingman"):
            return

        if message.guild.id not in self.is_available:
            self.is_available[message.guild.id] = True
            self.is_active[message.guild.id] = False

        if self.is_active[message.guild.id]:
            return

        for extra_wingman in self.extra_wingmen:
            if message.guild.id not in extra_wingman.is_available:
                extra_wingman.is_available[message.guild.id] = True

        command = message.content[9:]
        if command in ["$w", "$h", "$m", "$wg", "$hg", "$mg", "$wa", "$ha", "$ma"]:
            await self.roll_cmd(message, command)
        elif "$give" in command:
            await self.give_cmd(message, message.author, command)
        elif "$del" in command:
            await self.delete_cmd(message, command)
        elif "$leaderboard" in command:
            await message.channel.send((await self.get_channel(720106456724013128).history().get(author=self.user)).content)

    async def on_reaction_add(self, reaction, user):
        if not reaction.message.embeds or "Mudamaid" in user.name or "Mudae" in user.name:
            return

        if reaction.emoji not in ["❤️", "♥️", "💖", "💘", "💓", "💗", "💕"]:
            return

        for i in range(2, 7):
            if user.name == "TripleFury" + str(i):
                return

        self.loop.create_task(self.claim_cmd(reaction, user))
        # stop adding tasks after adding the first one

    async def delete_cmd(self, message, command):
        try:
            print(self.prefix + "Deleting " + command[5:] + " messages for " + message.author.name)
            await message.channel.purge(limit=int(command[5:]) + 1)
        except discord.Forbidden:
            print(self.prefix + "Forbidden")


    async def claim_cmd(self, reaction, user):
        def check(message):
            return "married" in message.content and user.name in message.content

        try:
            await self.wait_for("message", timeout=5, check=check)
        except asyncio.TimeoutError: # Claimed Unsuccessfully
            for extra_wingman in self.extra_wingmen:
                if await extra_wingman.claim(reaction.message, reaction, user):
                    break

    async def give_cmd(self, message, user, command):
        for extra_wingman in self.extra_wingmen:
            if await extra_wingman.give(message, user, command):
                break

    async def roll_cmd(self, message, command):
        guild_id = message.guild.id
        self.is_active[guild_id] = True

        if self.is_available[guild_id]:
            await message.channel.send("Have no fear **" + message.author.name + "**, The Waifu Wingmen are here to grant you more rolls!")
            await asyncio.sleep(1)

        helped = False
        for extra_wingman in self.extra_wingmen:
            if extra_wingman.is_available[guild_id] and extra_wingman.get_guild(guild_id) is not None:
                if await extra_wingman.roll(message, command):
                    await self.add_leaderboard(message.author)
                    helped = True
                    break

        if not helped:
            await asyncio.sleep(1)
            minutes_left = self.timer_time - datetime.datetime.now()
            await message.channel.send("Sorry, looks like all of the wingmen are unavailable 💔. Please try again in **" + str(math.ceil(minutes_left.seconds / 60)) + "** minutes.")

        self.is_active[guild_id] = False

    async def add_leaderboard(self, user):
        leaderboard_channel = self.get_channel(720106456724013128)
        message = await leaderboard_channel.history().get(author=self.user)
        message_lines = message.content.splitlines()

        leaders = {}

        for line in message_lines:
            if ")" in line:
                line_split = line.split(":")
                leaders[line_split[0].split(") ")[1]] = int(line_split[1])

        if user.name in leaders:
            leaders[user.name] += 1
        else:
            leaders[user.name] = 1

        sorted_leaders = {}
        for i in sorted(leaders, key=leaders.get, reverse=True):
            sorted_leaders[i] = leaders[i]
        leaders = sorted_leaders

        total = 0
        for leader in leaders:
            total += leaders[leader]

        final = "**Total Wingman Rolls**: `" + str(total) + "` ```\n"

        i = 0
        for leader in leaders:
            i += 1
            final += "{}) {}: {}\n".format(i, leader, str(leaders[leader]))

        final += "```"

        await message.edit(content=final)
