import discord
from discord.ext import commands

async def has_role(role):
    return False # This is temporary as /cogs/handlers/messageEvents.py uses it.

async def mention_or_fetch_user(ctx, argument): # TODO: Replace instances of this with discord.py built in typing, if that isn't done already.
    if ctx.message.mentions:
        return ctx.message.mentions[0]
    else:
        if ctx.args:
            try:
                user_id = int(argument)
                return await ctx.guild.fetch_member(user_id)
            except (ValueError):
                return await ctx.send("User not found.")
