import discord
from discord.ext import commands
import traceback
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import os



def has_role(role_id):
    async def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        role = discord.utils.get(ctx.author.roles, id=int(role_id))

        if role is not None:
            return True

        raise commands.MissingRole(f"You do not have the required role to use this command. (Role ID: {role_id})")

    return commands.check(predicate)

async def mention_or_fetch_user(ctx, argument):
    if ctx.message.mentions:
        return ctx.message.mentions[0]
    else:
        if ctx.args:
            try:
                user_id = int(argument)
                return await ctx.guild.fetch_member(user_id)
            except (ValueError):
                return await ctx.send("User not found.")
            
#ADD DB TO ERROR 
async def handle_error(err, ctx):
    db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
    errorDb = db["errors"]
    user_id = 529101675118592020
    user = ctx.guild.get_member(user_id)

    try:
        res = errorDb.find_one({"id": "err"})
        if user and res:
            errorCount = str(res["errorCount"]).zfill(3)
            # User found, send a DM
            full_error_message = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
            await user.send(f"Send by {ctx.author}\nMessage link: {ctx.message.jump_url}\nError code: {errorCount}\n```{full_error_message}```")
            await ctx.reply(f"**Error:** \n*Unexpected issue occurred in the advanced cognitive processes. *\n```javascript\nCode: SNAIL-ERR-HUMANS-{errorCount}\n```\nAre you now happy, humans?.")
        
        errorDb.find_one_and_update({"id": "err"}, {"$inc": {"errorCount": 1}})

    except Exception as e:
        print(f"Error handling failed: {e}")