# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
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



bot = Bot()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
load_dotenv()

bot.run(os.getenv("TOKEN"))
