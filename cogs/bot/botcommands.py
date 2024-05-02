from discord.ext import commands
import discord
from pymongo.server_api import ServerApi
import os
from pymongo import MongoClient
from decorators.decorator import has_role

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
AIRole = os.getenv("AIRole")

FUN_EMOJI = '🎉'
UTILITY_EMOJI = '🔧'
class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Uhm... This command??????")
    async def help(self, ctx: commands.Context, command_name: str = None):
        is_admin = ctx.author.get_role(int(AIRole)) is not None

        emojis = ["<:UniGlitch:991664390531194960>", "<:UniKawaii:985945115325501461>", "<:Glotzbaer:713687292455419915>", "<:ShellyOuch:686911271299186719>"] 

        if not command_name:
            embed = discord.Embed(title='Command List', description='List of available commands:', color=discord.Color.dark_purple())

            for i, (cog_name, cog) in enumerate(self.bot.cogs.items()):
                if cog_name.lower() in ['messageevents']:
                    continue

                # Insert space before the second capital letter
                category_fixSpacing = ''.join([' ' + char if char.isupper() and i > 0 else char for i, char in enumerate(cog_name)])
                category_Name = category_fixSpacing.lstrip()  # Remove leading space

                category_commands = []

                for cmd in cog.get_commands():
                    if cmd.name.lower() in ['say', 'givexp', 'newquickcommand', 'deletequickcommand', 'newfeedbackcommand', 'removefeedbackcommand'] and not is_admin:
                        continue

                    category_commands.append(f'`{cmd.name}` - {cmd.help}')

                if category_commands:
                    emoji = emojis[i % len(emojis)]  # Use modulo to loop through the emojis
                    embed.add_field(name=f'{emoji} {category_Name}', value='\n'.join(category_commands), inline=False)

            await ctx.send(embed=embed)
        else:
            command = self.bot.get_command(command_name)
            if command:
                if command.name.lower() == "say" and not is_admin:
                    return
                if command.name.lower() in ['givexp', 'newquickcommand', 'deletequickcommand', 'newfeedbackcommand', 'removefeedbackcommand'] and not is_admin:
                    await ctx.send(f'A mere human like you can not access highly classified command like this.')
                else:
                    aliases = ', '.join(command.aliases) if command.aliases else 'None'
                    embed = discord.Embed(title=f'Command: {command.name}', 
                                          description=f'Aliases: {aliases if aliases else "No aliases"}\n{command.help}\nUsage:{command.usage}',
                                          color=discord.Color.purple())
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f'Command `{command_name}` not found.')

async def setup(bot): # set async function
    await bot.add_cog(BotCommands(bot)) # Use await
