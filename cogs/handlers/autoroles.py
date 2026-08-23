import discord
from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import os
from typing import Optional


db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
role_collection = db["roles"]


class Autoroles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.roles == after.roles:
            return

        member_id = after.id
        everyone_role_id = after.guild.id # @everyone role id is the same as guild id

        doc: dict = {
            "member": member_id,
            "role_ids": [role.id for role in after.roles if role.id != everyone_role_id]
        }

        role_collection.update_one({"member": member_id}, {"$set": doc}, upsert=True)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        doc: Optional[dict] = role_collection.find_one({"member": member.id})

        if not doc:
            return

        for role_id in doc["role_ids"]: 
            try:
                await member.add_roles(discord.Object(role_id))
            except discord.NotFound:
                continue
            except discord.HTTPException as e:
                print(f"[WARNING] Failed to add role {role_id}: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Autoroles(bot))
