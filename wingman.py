import discord
import asyncio
import os
import datetime
import random


class Wingman(discord.Client):
    loop = asyncio.get_event_loop()

    def __init__(self, number):
        self.prefix = "TripleFury" + str(number + 1) + ": "
        self.is_available = {}

        self.loop.create_task(self.start(os.getenv("token" + str(number)), bot=False))
        super().__init__()
        print(self.prefix + "Initializing...")

    async def on_ready(self):
        #await self.change_presence(activity=discord.Game("$wingman $w | $h | $m"))
        await self.change_presence(activity=discord.Game("❤️"))

        print(self.prefix + "Logged in as " + self.user.name + " (" + str(self.user.id) + ")")

        # Seconds until midnight
        dt = datetime.datetime.utcnow()
        await asyncio.sleep(((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second) + (2 * int(self.prefix[10])))

        print(self.prefix + "Getting daily kakera")
        waifu_channel = self.get_channel(720088956938485841)
        await waifu_channel.send("$dk")

    async def claim(self, message, reaction, user):
        channel = self.get_channel(message.channel.id)

        async for msg in channel.history(): # Replacement for channel.fetch_message()
            if msg.id == message.id:
                message = msg
                break

        waifu = message.embeds[0].author.name

        print(self.prefix + "Attempting to claim " + waifu + " for " + user.name)

        await message.add_reaction(reaction.emoji)

        def check(message):
            return "married" in message.content and self.user.name in message.content

        try:
            await self.wait_for("message", timeout=2, check=check)
        except asyncio.TimeoutError:  # Claimed Unsuccessfully
            return False
        else: # Claimed Successfully
            await channel.send("Successfully claimed **" + waifu + "** for **" + user.name + "**! Use $wingman $give <character> to receive your claim!")
            await self.give(message, user, "$give " + waifu)
            return True

    async def give(self, message, user, command):
        channel = self.get_channel(message.channel.id)

        await asyncio.sleep(1)

        waifu = command[6:]
        msg = await channel.send("$give " + user.mention + " " + waifu)

        def check(message):
            return "Who" in message.content

        try:
            msg2 = await self.wait_for("message", timeout=2, check=check)
        except asyncio.TimeoutError: # Successful
            print(self.prefix + "Offered " + waifu + " to " + user.name)
            return True
        else: # Unsuccessful
            await channel.send("$exit", delete_after=2)

            try:
                await (await self.wait_for("message", timeout=2)).delete()
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(1)
            await msg.delete()
            await msg2.delete()

            return False

    async def roll(self, message, command):
        channel = self.get_channel(message.channel.id)
        guild_id = message.guild.id

        from main_wingman import MainWingman
        MainWingman.is_active[guild_id] = True

        author = message.author.name
        og_message = message
        success = False

        print(self.prefix + "Attempting to roll for " + author + " in " + message.guild.name)

        await asyncio.sleep(1)

        while self.is_available[guild_id]:
            limited = "**" + self.user.name + "**, the roulette is limited"
            disabled = "Command DISABLED"
            restricted = "Command RESTRICTED"

            if disabled in message.content or restricted in message.content:
                return True

            if limited in message.content:
                self.is_available[guild_id] = False

                if not success:
                    author = "Unknown"
                    # reply = "Looks like you didn't actually get any rolls. Calling for backup..."

                await self.change_presence(status=discord.Status.dnd, activity=discord.Game("💔 by " + author))
                self.loop.create_task(self.set_timer(message))
                break

            else:
                await channel.send(command, delete_after=2)
                try:
                    message = await self.wait_for("message", timeout=5)
                except asyncio.TimeoutError:
                    print(self.prefix + "Timed out, sending another roll...")
                    await channel.send(command, delete_after=2)

                await asyncio.sleep(random.randint(1, 2))

                if message.embeds:
                    success = True
                    #self.is_available[guild_id] = False
                    #break

        if success:
            MainWingman.is_active[guild_id] = False

            print(self.prefix + "Successfully rolled for " + author)
            reply = "Successfully rolled for **" + author + "**!"

            available_wingmen = 0
            for extra_wingman in MainWingman.extra_wingmen:
                if extra_wingman.is_available[guild_id]:
                    available_wingmen += 1

            if available_wingmen > 0:
                reply += " There are **" + str(available_wingmen) + "** more wingmen available. If you would like me to continue rolling, please react to this message!"
                message = await channel.send(reply)

                async def react_roll():
                    try:
                        await message.add_reaction("💖")

                        def check(reaction, user):
                            return str(reaction.emoji) == "💖" and reaction.message.content == message.content and user.name == author
                        await self.wait_for("reaction_add", timeout=15, check=check)
                    except asyncio.TimeoutError:
                        print(self.prefix + "Reaction timed out")
                    else: # Reaction Success
                        if not MainWingman.is_active[guild_id]:
                            await MainWingman.roll_cmd(MainWingman.extra_wingmen[0], og_message, command)

                self.loop.create_task(react_roll())

            else:
                reply += " There are no more wingmen available 💔. Please try again later."
                message = await channel.send(reply)

        return success

    async def set_timer(self, message):
        index = message.content.find("min left")
        minutes = int("".join(filter(str.isdigit, message.content[index - 5:index])))
        seconds = datetime.datetime.now().second

        from main_wingman import MainWingman
        MainWingman.timer_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

        print(self.prefix + "Unavailable for " + str(minutes) + " minutes")

        await asyncio.sleep(minutes * 60 - int(seconds))
        print(self.prefix + "Now Available")
        self.is_available[message.guild.id] = True
        await self.change_presence(status=discord.Status.online, activity=discord.Game("❤️"))
