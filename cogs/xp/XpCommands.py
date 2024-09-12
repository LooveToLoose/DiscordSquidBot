import os
import discord
import datetime
import asyncio
from discord.ext import commands, tasks
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import typing
import time
import random
import math
import json

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
xpCollection = db["newerxps"]
optoutCollection= db["bools"]
AIRole = int(os.getenv("AIRole"))

class XpCommand(commands.Cog):
    user_cooldowns = {}
    
    def __init__(self, bot):
        with open("json/xp.json", "r") as file:
            data = json.load(file)
            self.min_xp = data["min_xp"]
            self.max_xp = data["max_xp"]

            self.level_rewards = data["level_rewards"]

            self.level_rewards.sort(key=lambda r: r["level"])
            
            self.after_last_emoji = data["last_emoji"]

            self.level_ups_channel_id = data["level_ups_channel"]

        self.remove_old_cooldowns.start()
            
        self.bot = bot

    async def cog_unload(self):
        self.remove_old_cooldowns.cancel()


    ##ADMIND COMMANDS
    @commands.command(name="givexp", 
                      help="Give user xp", 
                      usage="sq!addxp @user/userID XpAmount")
    @commands.has_role(AIRole)
    async def givexp(self, ctx:commands.Context, member: typing.Optional[discord.Member], amount_of_xp: int):
        user = member if member is not None else ctx.author
        if not isinstance(user, discord.Member): return
        if not ctx.guild: return
        
        embed = discord.Embed(
            title="Giving XP",
            timestamp=ctx.message.created_at
        )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

        embed.add_field(name="From", value=ctx.author.display_name, inline=True)
        embed.add_field(name="To", value=user.display_name, inline=True)
        embed.add_field(name="Amount", value=amount_of_xp, inline=True)

        await self.add_xp(user, amount_of_xp)
        
        embed.set_footer(text=ctx.guild.name)
        await ctx.send(embed=embed)

    #USER COMMANDS
    @commands.command(name="xp", 
                      help="Get your or someones elses xp", 
                      aliases=['showxp'],
                      usage="sq!xp (@user/userID)")
    async def showXp(self, ctx: commands.Context, user: typing.Optional[discord.Member]):
            if not user:
                user = ctx.author

            res = xpCollection.find_one({"UserId": str(user.id)})
            
            if res is None:
                await ctx.reply("It looks like this user doesn't like talking")
                return

            current_level = self.calc_level_for_xp(res["Xp"])
            next_level_xp = self.calc_xp_for_level(current_level + 1)

            embed = discord.Embed(
                title="XP Info",
                color=discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.set_author(name=user.display_name, icon_url=user.avatar)
            if user.avatar:
                embed.set_thumbnail(url=user.avatar)    

            level_emoji = self.level_rewards[0]["emoji"]
            next_level_emoji = self.after_last_emoji
            
            for reward in self.level_rewards:
                if current_level >= reward["level"]:
                    level_emoji = reward["emoji"]
                else:
                    next_level_emoji = reward["emoji"]
                    break

            embed.add_field(
                name="XP", 
                value=f"{res['Xp']:,}"
            )
                
            embed.add_field(
                name=f"{level_emoji} **Level**", 
                value=f'`{current_level}`'
                )
#            embed.add_field(name='\u200b',value='\u200b')
            embed.add_field( # Next Level, next emoji
                name=f"{next_level_emoji} **Next Level**", 
                value=f'`{res["Xp"]:,}` / `{next_level_xp:,}` (`{next_level_xp-res["Xp"]}`)',
                inline=False
            )

            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar)

            await ctx.send(embed=embed)
        
    @commands.command(name="xptop", 
                      help="See who has the biggest ego",
                      usage="sq!xptop (page number)")
    async def xpTop(self, ctx: commands.Context, page_num: int = 1):
        commands_info = []
        res = xpCollection.find({}).sort("Xp", -1)

        for doc in res:
            try:
                shortName = doc["ShortName"]
            except KeyError as e:
                shortName = "Quitter"
            
            user = ctx.guild.get_member(int(doc["UserId"]))

            if user is not None:
                commands_info.append((user.id, doc["Xp"], self.calc_level_for_xp(doc["Xp"]), shortName))

        else:
            page_size = 5 
            total_pages = (len(commands_info) + page_size - 1) // page_size

            # Check if the provided page number is valid
            if page_num < 1 or page_num > total_pages:
                await ctx.send("Invalid page number. Please enter a valid page number.")
                return

            current_page = page_num - 1

            async def generate_embed(page):
                embed = discord.Embed(
                    title="Xp Leaderboards",
                    color=discord.Color.purple()
                )
                embed.clear_fields()

                embed.set_thumbnail(url=ctx.guild.icon)
                start_idx = page * page_size
                end_idx = min((page + 1) * page_size, len(commands_info))

                for index,data in enumerate(commands_info[start_idx:end_idx]):
                    
                    
                    userShortName = await self.bot.fetch_user(data[0])

                    if(current_page > 0):
                        position = (index + 1) + (page_size * current_page)
                    else:
                        position = index + 1  

                    emoji = ""

                    if position == 1:
                        emoji = "<:ShellyDiamond:717472682341433472>"
                    elif position == 2:
                        emoji = "<:ShellyGold:710586809712640012>"
                    elif position == 3:
                        emoji = "<:ShellySilver:710586793132818530>"
                    elif position == 4:
                        emoji = "<:ShellyBronze:710586775319478312>"
                    else:
                        emoji = "<:ShellySnail:710586732097044490>"

                    formatted_xp = f"{data[1]:,}"
                    
                    embed.add_field(
                        name=f"{emoji} **{position}. {userShortName.display_name}**", 
                        value=f"**Xp** `{formatted_xp}` \n **Level** `{data[2]}`", 
                        inline=False)
            
                        
                    embed.set_footer(text=f"Page {page + 1}/{total_pages}")
                    #embed.set_thumbnail(url=self.bot.avatar_url)

                return embed

            message = await ctx.send(embed=await generate_embed(current_page))

            buttons = [
                "<:left:1158778793687781397>",
                "<:right:1158778827435167834>", 
            ]

            for button in buttons:
                await message.add_reaction(button)

            def check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji) in buttons
                    and reaction.message.id == message.id
                )

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)

                    if str(reaction.emoji) == "<:left:1158778793687781397>" and current_page > 0:
                        current_page -= 1
                    elif str(reaction.emoji) == "<:right:1158778827435167834>" and current_page < total_pages - 1:
                        current_page += 1

                    await message.edit(embed= await generate_embed(current_page))
                    await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    break

    @commands.command(name="optout",
                      help="Turn off/on pings when leveling up",
                      usage="sq!optout")
    async def optout(self, ctx:commands.Context):
        # Try to find the user's data in the database
        data = optoutCollection.find_one({"userID": ctx.author.id})

        if not data:
            # If the user does not exist in the database, create a new entry
            new_data = {
                "name": ctx.author.display_name,
                "optout": True,
                "userID": ctx.author.id
            }
            optoutCollection.insert_one(new_data)
            response = "You will now not be pinged when you level up!"
        else:
            if data["optout"]:
                data["optout"] = False
                optoutCollection.update_one({"userID": ctx.author.id}, {"$set": {"optout": False}})
                response = "You will now be pinged when you level up!"
            else:
                data["optout"] = True
                optoutCollection.update_one({"userID": ctx.author.id}, {"$set": {"optout": True}})
                response = "You will now not be pinged when you level up!"

        await ctx.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None or not isinstance(message.author, discord.Member): return

        if (message.author.id in self.user_cooldowns
            and time.time() <= self.user_cooldowns[message.author.id]):
            return
        
        self.user_cooldowns[message.author.id] = time.time() + 60
        # MAYBE: Check for yo and only give 1 xp? idk, we'll see.
        added_xp = random.randint(self.min_xp, self.max_xp)
        await self.add_xp(message.author, added_xp)

    async def add_xp(self, user: discord.Member,  xp: int, force_give_roles: bool = False ):
        res = xpCollection.find_one_and_update(
            {"UserId": f"{user.id}"},
            {'$inc': {'Xp': xp}},
            upsert=True)

        if res is None:
            res = {"Xp": 0}
            
        current_level = self.calc_level_for_xp(res["Xp"] + xp)
        old_level = self.calc_level_for_xp(res["Xp"])

        if current_level == old_level and (not force_give_roles):
            return
        
        current_roles = [role.id for role in user.roles]
        to_add = [reward['role'] for reward in self.level_rewards if reward['level'] <= current_level]
        to_add = [user.guild.get_role(role) for role in to_add if role not in current_roles]
        to_remove = [reward['role'] for reward in self.level_rewards if reward['level'] > current_level]
        to_remove = [user.guild.get_role(role) for role in to_remove if role in current_roles]
        if len(to_add) != 0: await user.add_roles(*to_add)
        if len(to_remove) != 0: await user.remove_roles(*to_remove)

        if current_level > old_level:
            channel = user.guild.get_channel(self.level_ups_channel_id)
            if not isinstance(channel, discord.TextChannel): return

            data = optoutCollection.find_one({"userID": user.id})
            await channel.send(f"🎉 Congratulations {user.mention if data and data['optout'] else user.name}, you've leveled up! Your new Level is **{current_level}**.")

    def calc_level_for_xp(self, xp: int) -> int:
        mult = -1 if xp < 0 else 1
        xp *= mult
        return math.floor(math.sqrt((xp/5)+25)-5) * mult

    def calc_xp_for_level(self, level: int) -> int:
        if level < 0: return self.calc_xp_for_level(-level) * -1
        return 5*(level*level + level * 10)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.add_xp(member, 0, True)

    @tasks.loop(seconds=120.0)
    async def remove_old_cooldowns(self):
        to_remove = []
        for userid, cooldown in self.user_cooldowns.items():
            if time.time() > cooldown:
                to_remove.append(userid)
        for user in to_remove:
            del self.user_cooldowns[user]

    
async def setup(bot): # set async function
    await bot.add_cog(XpCommand(bot)) # Use await
