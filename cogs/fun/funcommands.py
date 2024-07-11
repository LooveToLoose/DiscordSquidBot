import discord
from discord.ext import commands
import random
from pymongo.server_api import ServerApi
import json 
import traceback
import time
import os
from pymongo import MongoClient
import platform
import decorators.decorator as dc

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
AIRole = os.getenv("AIRole")
yoCollection = db["yos"]
class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

     #ADMIN COMMANDS
    @commands.command(name="say", 
                      role="Admin", 
                      help="Say something while being Squid",
                      usage="sq!say")
    @dc.has_role(AIRole)
    async def say(self, ctx: commands.Context,*, message):
        if not message:
            await ctx.send('Specify what you want to say!')
            return

        text_channel_mentions = ctx.message.channel_mentions
        if text_channel_mentions:
            text_channel = text_channel_mentions[0]
            if message.startswith(text_channel.mention):
                message = message[len(text_channel.mention):].strip() 
            await text_channel.send(message)
        else:
            await ctx.send(message)

        await ctx.message.delete()


    @commands.command(name="ask", 
                      role="Everyone", 
                      help="Ask me something",
                      usage="sq!ask question")
    async def ask(self, ctx: commands.Context):
        # Load your answers from a JSON file
        with open('././json/answers.json', 'r') as file:
            data = json.load(file)

        answers = data['answers']
        who = data['who']
        what = data['what']
        when = data['when']
        should = data['should']
        why = data['why']

        # Check the content of the message and respond accordingly
        content = ctx.message.content.lower()
        if "who" in content:
            response = random.choice(who)
        elif "what" in content:
            response = random.choice(what)
        elif "when" in content:
            response = random.choice(when)
        elif "should" in content:
            response = random.choice(should)
        elif "why" in content:
            response = random.choice(why)
        else:
            response = random.choice(answers)

        await ctx.reply(response)


    @commands.command(name="status", 
                      help="Do NOT check my status..",
                      usage="sq!status")
    async def status(self, ctx: commands.Context):
        uptime_seconds = int(time.time() - 0)
        uptime = time.strftime('%Hh %Mm %Ss', time.gmtime(uptime_seconds))

        await ctx.send("Calculating info...")
        ping = round(self.bot.latency * 1000)

        status_embed = discord.Embed(
            color=discord.Color.purple()
        )
            
        status_embed.set_thumbnail(url=self.bot.user.avatar)
        status_embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url
        )

        status_embed.add_field(
            name="Discord.py Version",
            value=f"`{discord.__version__}`",
        )

        status_embed.add_field(
            name="Python Version",
            value=f"`{platform.python_version()}`",
            inline=True
        )

        status_embed.add_field(name='\u200b',value='\u200b')
    
        status_embed.add_field(
            name="🕒 Uptime",
            value=f"{uptime}",
        )

        status_embed.add_field(
            name="🏓 Ping",
            value=f"{ping}ms",
            inline=True
        )
        await ctx.send("Found info!", embed=status_embed)


    @commands.command(name="yocount",  
                      help="See how simple you humans are in terms of intelligence.",
                      usage="sq!yocounter")
    async def yocount(self,ctx: commands.Context):
        yoCount = yoCollection.find_one({"word": "yo"})
        await ctx.send(f"Yo has been said {yoCount['yo']:,} times.")

    @commands.command(name="avatar",
                      help="Get your or someone elses avatar",
                      usage="sq!avatar (@user or userId)")
    async def avatar(self,ctx, *args):
        if args:
            user = await dc.mention_or_fetch_user(ctx,args[0])
        else:
            user = ctx.author

        avatar_url = user.avatar

        if user.id != 1149390145745862766:
            embed = discord.Embed(
                title=f"{user.display_name}'s avatar",
                color=discord.Color.random()
            )
        else:
            embed = discord.Embed(
                title=f'My avatar',
                description="He.. hehehe....",
                color=discord.Color.purple()
            )
        
        embed.set_image(url=avatar_url)
        await ctx.reply(embed=embed)


class ErrorHandling():
    @FunCommands.say.error
    async def say_error(self,ctx,error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('Inccorrect arguments entered | !command_name - channel - msg')
async def setup(bot): # set async function
    await bot.add_cog(FunCommands(bot)) # Use await