import os
import discord
import datetime
import traceback
import asyncio
import locale
from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import typing

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
xpCollection = db["newerxps"]
optoutCollection= db["bools"]
AIRole = int(os.getenv("AIRole"))

class XpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    ##ADMIND COMMANDS
    @commands.command(name="givexp", 
                      help="Give user xp", 
                      usage="sq!addxp @user/userID XpAmount")
    @commands.has_role(AIRole)
    async def addXp(self, ctx:commands.Context, member: typing.Optional[discord.Member], amount_of_xp: int):
        user = member if member is not None else ctx.author
        if not amount_of_xp:
            await ctx.reply("Please specify the amount of XP you want to add/subtract!")
            return

        if not isinstance(amount_of_xp, int):
            await ctx.reply("Invalid number!")
            return

        embed = discord.Embed(
            title="Giving XP",
            timestamp=ctx.message.created_at
        )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

        embed.add_field(name="From", value=ctx.author.display_name, inline=True)
        embed.add_field(name="To", value=user.display_name, inline=True)
        embed.add_field(name="Amount", value=amount_of_xp, inline=True)

        user_id = str(user.id)

            # Retrieve XP data from MongoDB
        xp_data = xpCollection.find_one({"UserId": user_id})

        if not xp_data:
            xp_data = {
                "UserId": user_id,
                "Xp": amount_of_xp,
                "Level": 1,
                "ShortName": user.display_name
            }
            xpCollection.insert_one(xp_data)
        else:
            xp_data["Xp"] += amount_of_xp
            
            for _ in range(30):
                next_level = xp_data["Level"] + 1
                new_level = 100 * next_level * next_level / 20 + next_level * 50
                if xp_data["Xp"] >= new_level:
                    xp_data["Level"] += 1

            xpCollection.replace_one({"UserId": user_id}, xp_data)
            print(xp_data["Level"])  

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

            myquery = { "UserId": str(user.id) }
            if (xpCollection.count_documents(myquery) != 0):
                res = xpCollection.find().sort("Xp", -1)
                for index, result in enumerate(res):

                    if(result["UserId"]== str(user.id)):
                        xp = result["Xp"]
                        level = result["Level"]

                        embed = discord.Embed(
                            title="XP Info",
                            color=discord.Color.random(),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_author(name=user.display_name, icon_url=user.avatar)
                        if user.avatar:
                            embed.set_thumbnail(url=user.avatar)    
                    

                        nxtLvl = level + 1
                        newLevel = int(100 * nxtLvl * nxtLvl / 20 + nxtLvl * 50)
                        LevelXp = int(newLevel - xp)

                        embed.add_field(
                            name="XP", 
                            value=f"{xp:,}"
                            )
                        
                        if level >= 150:
                            embed.add_field(
                                name="<:ShellyDiamond:717472682341433472> **Level**", 
                                value=f'`{level}`', 
                                inline=True)
                            
                            embed.add_field(name='\u200b',value='\u200b')
                            embed.add_field(
                                name="<:shellyprototype:981954824851562497>  **Next Level**", 
                                value=f'`{xp:,}` / `{newLevel:,}` (`{LevelXp}`)')
                        elif level >= 100:
                            embed.add_field(
                                name="<:ShellyGold:710586809712640012> **Level**", 
                                value=f'`{level}`', 
                                inline=True)
                            embed.add_field(name='\u200b',value='\u200b')
                            embed.add_field(
                                name="<:ShellyDiamond:717472682341433472> **Next Level**", 
                                value=f'`{xp:,}` / `{newLevel:,}` (`{LevelXp}`)')
                        elif level >= 50:
                            embed.add_field(
                                name="<:ShellySilver:710586793132818530> **Level**", 
                                value=f'`{level}`', 
                                inline=True)
                            embed.add_field(name='\u200b',value='\u200b')
                            embed.add_field(
                                name="<:ShellyGold:710586809712640012> **Next Level**", 
                                value=f'`{xp:,}` / `{newLevel:,}` (`{LevelXp}`)')
                        elif level >= 25:
                            embed.add_field(
                                name="<:ShellyBronze:710586775319478312>  **Level**", 
                                value=f'`{level}`', 
                                inline=True)
                            embed.add_field(
                                name="<:ShellySilver:710586793132818530> **Next Level**", 
                                value=f'`{xp:,}` / `{newLevel:,}` (`{LevelXp}`)')
                        elif level <= 25:
                            embed.add_field(
                                name="<:ShellyBronze:710586775319478312>  **Level**", 
                                value=f'`{level}`', 
                                inline=True)
                            embed.add_field(name='\u200b',value='\u200b')

                            embed.add_field(
                                name="<:ShellySilver:710586793132818530> **Next Level**", 
                                value=f'`{xp:,}` / `{newLevel:,}` (`{LevelXp}`)')
                            
                        embed.add_field(
                            name="LB pos.",
                            value=f"{index + 1} / {xpCollection.count_documents({})}",
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
                commands_info.append((user.id, doc["Xp"], doc["Level"], shortName))

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
        
async def setup(bot): # set async function
    await bot.add_cog(XpCommand(bot)) # Use await
