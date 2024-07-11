import discord
from discord.ext import commands

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