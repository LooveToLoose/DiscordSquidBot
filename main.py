# This example requires the 'message_content' intent.

import traceback
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient

load_dotenv(override=True)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=[prefix.strip() for prefix in os.getenv("PREFIXES").split(",")], intents=discord.Intents.all())
        self.remove_command("help")
    async def startup(self):
        await bot.wait_until_ready()
        await bot.tree.sync()  # If you want to define specific guilds, pass a discord object with id (Currently, this is global)
        print('Sucessfully synced applications commands')
        print(f'Connected as {bot.user}')

    async def setup_hook(self):
        for folder in os.listdir("./cogs"):
            if os.path.isdir(f"./cogs/{folder}"):
                for filename in os.listdir(f"./cogs/{folder}"):
                    if filename.endswith(".py"):
                        try:
                            await bot.load_extension(f"cogs.{folder}.{filename[:-3]}")
                            print(f"Loaded {filename}")
                        except Exception as e:
                            print(f"Failed to load {filename}")
                            print(f"[ERROR] {e}")

        self.loop.create_task(self.startup())

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound): return

        if isinstance(error, commands.UserInputError):
            await ctx.send(f'Incorrect argument | Usage: {ctx.command.usage}')
            return
        
        if isinstance(error, commands.MissingRole):
            await ctx.reply("You aren't allowed to use this command!")
            return
        
        db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
        errorDb = db["errors"]
        user_id = 391234130387533825
        user = ctx.guild.get_member(user_id)

        try:
            res = errorDb.find_one({"id": "err"})
            errorDb.insert_one
            if not res:
                errorDb.insert_one({"id": "err", "errorCount": 0})
                res = errorDb.find_one({"id": "err"})
            if user and res:
                errorCount = str(res["errorCount"]).zfill(3)
                # User found, send a DM
                full_error_message = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
                await user.send(f"Send by {ctx.author}\nMessage link: {ctx.message.jump_url}\nError code: {errorCount}\n```{full_error_message}```")
                await ctx.reply(f"**Error:** \n*Unexpected issue occurred in the advanced cognitive processes. *\n```javascript\nCode: SNAIL-ERR-HUMANS-{errorCount}\n```\nAre you now happy, humans?.")
            
            errorDb.find_one_and_update({"id": "err"}, {"$inc": {"errorCount": 1}})

        except Exception as e:
            print(f"Error handling failed: {e}")



bot = Bot()


bot.run(os.getenv("TOKEN"))
