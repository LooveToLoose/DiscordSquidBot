import os
import discord
import asyncio

from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
collection = db["quick commands"]


AIRole = int(os.getenv("AIRole"))

class QuickCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deletequickcommand", 
                      aliases=["dqc","removequickcommand","rqc"], 
                      help="Remove a quick command!",
                      usage="sq!dqc commandName")
    @commands.has_role(AIRole)
    async def deletequickcommand(self, ctx:commands.Context, command_name):
        result = collection.find_one_and_delete({"commandName": command_name.lower()})

        if result is None:
            await ctx.send(f"The quick command you are trying to delete doesn't exist!")
        else:
            await ctx.send(f"The quick coommand named {command_name} deleted!")

    @commands.command(name="newquickcommand", 
                      aliases=["nqc","addquickcommand","aqc"], 
                      help="Add a quick command!",
                      usage="sq!nqc commandName response")
    @commands.has_role(AIRole)
    async def newquickcommand(self,ctx:commands.Context, command_name, *response):
        if not command_name:
            return await ctx.reply("Please specify a command name!")
            
        command_response = " ".join(response)
        if not command_response:
            return await ctx.reply("Please specify a command answer!")

        data = collection.find_one({"commandName": command_name})
        if not data:
            new_data = {
                "commandName": command_name,
                "commandRespond": command_response,
                "createdBy": ctx.author.id
            }
            collection.insert_one(new_data)
            await ctx.reply(f"New command created! Name: {command_name}")
        else:
            await ctx.reply("Command with this name already exists!")

    @commands.command(name="getquickcommands", 
                      aliases=["quickcommands","qc","gqc"], 
                      help="Get all quick commands!",
                      usage="sq!gqc")
    async def getquickcommands(self, ctx: commands.Context):
        commands_info = []
        res = collection.find({})

        for doc in res:
            commands_info.append((doc["commandName"], doc["commandRespond"]))

        if not commands_info:
            await ctx.reply("There aren't any quick commands!")
        else:
            page_size = 5 
            current_page = 0
            total_pages = (len(commands_info) + page_size - 1) // page_size

            def generate_embed(page):
                embed = discord.Embed(
                    title="Quick Commands",
                    description=f"Page {page + 1}/{total_pages}",
                    color=discord.Color.blue()
                )

                start_idx = page * page_size
                end_idx = min((page + 1) * page_size, len(commands_info))

                for cmd, desc in commands_info[start_idx:end_idx]:
                    embed.add_field(name=cmd, value=desc, inline=False)

                return embed

            message = await ctx.send(embed=generate_embed(current_page))

            buttons = [
                "<:Left:1286702311661375519>",
                "<:Right:1286702326274592788>",
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

                    if str(reaction.emoji) == "<:left:1286702311661375519>" and current_page > 0:
                        current_page -= 1
                    elif str(reaction.emoji) == "<:right:1286702326274592788>" and current_page < total_pages - 1:
                        current_page += 1

                    await message.edit(embed=generate_embed(current_page))
                    await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    break


async def setup(bot): # set async function
    await bot.add_cog(QuickCommands(bot)) # Use await
