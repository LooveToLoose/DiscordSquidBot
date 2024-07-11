import os
import discord
import asyncio

from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import decorators.decorator as dc

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
collection = db["feedback commands"]

AIRole = os.getenv("AIRole")

class FeedbackCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="removefeedbackcommand", 
                      aliases=["rfc","deletefeedbackcommand","dfc"], 
                      help="Remove a feedback command!", 
                      usage="sq!rfc commandName")
    @dc.has_role(AIRole)
    async def removefeedbackcommand(self,ctx:commands.Context, command_name):
        if not command_name:
            return await ctx.send("Please specify a feedback command name!")

        result = collection.find_one_and_delete({"commandName": command_name.lower()})

        if result is None:
            return await ctx.send(f"The feedback command you are trying to delete doesn't exist!")
        else:
            return await ctx.send(f"Feedback command named {command_name} deleted!")

    @commands.command(name="newfeedbackcommand", 
                      aliases=["nfc","addfeedbackcommand","afc"], 
                      help="Add a feedback command!",
                      usage="sq!nfc commandName #textChannel @roleThatCanUse")
    @dc.has_role(AIRole)
    async def newfeedbackcommand(self,ctx:commands.Context, command_name, text_channel: discord.TextChannel, role: discord.Role):
        if not command_name:
            return ctx.send("Please specify a command name!")

        if not text_channel:
            return ctx.send("Tag a text channel please!")

        if not role:
                return ctx.send("Invalid role that can use this command!")

        existing_command = collection.find_one({"commandName": command_name})
        if existing_command:
            await ctx.reply("Command with this name already exists!")
            return

        # Save the new command data to MongoDB
        new_command = {
            "commandName": command_name,
            "channelID": text_channel.id,
            "roleThatCanUse": role.id,
            "createdBy": ctx.author.id
        }
        collection.insert_one(new_command)

        await ctx.reply(f"New command created! Name: {command_name}")

    @commands.command(name="getfeedbackcommands", 
                      aliases=["feedbackcommands","fc","gfc"],
                      help="Get all feedback commands",
                      usage="sq!gfc")
    async def getfeedbackcommands(self, ctx:commands.Context):
        commands_info = []
        res = collection.find({})

        for doc in res:
            command_name = doc["commandName"]
            channel_id = doc["channelID"]
            role_that_can_use = doc["roleThatCanUse"]

            # Get user, channel, and role objects
            channel = ctx.guild.get_channel(int(channel_id))
            role = ctx.guild.get_role(int(role_that_can_use))

            # Create embed fields
            fields = [
                ("Command Name", command_name, True),
                ("Channel", f"[{channel.name}](https://discord.com/channels/{ctx.guild.id}/{channel_id})" if channel else "Unknown Channel", True),
                ("Role That Can Use", f"{role.name}" if role else "Unknown Role", True),
            ]

            commands_info.append(fields)

        if not commands_info:
            await ctx.reply("There aren't any quick commands!")
        else:
            page_size = 5
            current_page = 0
            total_pages = (len(commands_info) + page_size - 1) // page_size

            def generate_embed(page):
                embed = discord.Embed(
                    title="Feedback Commands",
                    description=f"Page {page + 1}/{total_pages}",
                    color=discord.Color.blue()
                )

                start_idx = page * page_size
                end_idx = min((page + 1) * page_size, len(commands_info))

                for fields in commands_info[start_idx:end_idx]:
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                return embed

            message = await ctx.send(embed=generate_embed(current_page))

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

                    await message.edit(embed=generate_embed(current_page))
                    await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    break

class ErrorHandling():
    @FeedbackCommands.removefeedbackcommand.error
    async def removefeedbackommand_error(self,ctx,error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('Inccorrect arguments entered | !command_name - name')
    @FeedbackCommands.newfeedbackcommand.error
    async def newfeedbackcommand_error(self,ctx,error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('Inccorrect arguments entered | !command_name - name - text channel - role')
async def setup(bot): # set async function
    await bot.add_cog(FeedbackCommands(bot)) # Use await