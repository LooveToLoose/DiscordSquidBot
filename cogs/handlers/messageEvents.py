from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import discord
import os
import time
import random
import asyncio
from decorators.decorator import has_role

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
xpCollection = db["newerxps"]
yoCollection = db["yos"]
quickCommandsCollection = db["quick commands"]
feedbackCommandsCollection = db["feedback commands"]
levelsCollection = db["levels"]
boolsCollection = db["bools"]


user_cooldowns = {}
maxXP = 16
minXP = 7

AIRole = os.getenv("AIRole")
prefixes = "!"
buttons = ["<:Diff1InfinitelyEasy:686910602689380422>",
           "<:Down:946437519476666379>"]

for result in levelsCollection.find({"id": "levels"}):
    cs_level = result["ConfirmedSnail"]
    as_level = result["AdvancedSnail"]
    bs_level = result["BestSnail"]
    gs_level = result["GodlikeSnail"]
    gods_level = result["GodSnail"]

class messageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        
        #QUICK COMMANDS / FEEDBACK COMMANDS

        if (message.content.startswith(prefixes)):
            await QuickOrFeedbackCommands(message=message)
            return



               

        ############
        #YO SYSTEM
        await yoSystem_Handler(message)

        ##############
        #XP SYSTEM
        if user_id in user_cooldowns and time.time() - user_cooldowns[user_id] < 60:  # 1 minute cooldown
            return
        
        await xpSystem_Handler(user_id, message)
        ###################

        
            
    
#### MAIN HANDLERS #####

async def yoSystem_Handler(message):
        yo_variations = ["yo", "Yo!", "yoy", "yoyo","<:YO:714280062437818559>","oy","<:yonas:741360791667605596>", "<:YoBoss:787408970792697876>", "<:SquidYo:714937825518157905>","<:shellyo:741359253050097674>"]

        #check if message contains words in
        content = message.content.lower()
        if any(variation in content for variation in yo_variations):
            yoCollection.find_one_and_update({"word":"yo"}, {"$inc":{"yo": 1}})
           
async def xpSystem_Handler(user_id, message):
        
        
        myquery = { "UserId": f"{user_id}" }
        if (xpCollection.count_documents(myquery) != 0):
            cooldown_duration = random.randint(30, 60)
            user_cooldowns[user_id] = time.time() + cooldown_duration

            xpAdd = round(random.random() * (maxXP - minXP)) + minXP
            
            for result in xpCollection.find(myquery):
                xp =  result["Xp"]
                level = result["Level"]
            
            newXp = xp + xpAdd
            nxtLvl = level + 1
            newLevel = 100 * nxtLvl * nxtLvl / 20 + nxtLvl * 50
            
            lvl_up_channel = discord.utils.get(message.guild.channels, name="level-ups")

            if(newXp >= newLevel):
                level += 1
                await check_if_user_has_level_role(message,level)
                res = boolsCollection.find_one({"userID": f"{message.author.id}"})

                if res:
                    optout = res.get("optout", False)  # Get the 'optout' key or default to False if not found
                    if not optout:
                        await lvl_up_channel.send(f'🎉 Congratulations {message.author.mention} you\'ve leveled up! Your new Level is **{level}**.')
                    else:
                        await lvl_up_channel.send(f'🎉 Congratulations {message.author} you\'ve leveled up! Your new Level is **{level}**.')
                else:
                    await lvl_up_channel.send(f'🎉 Congratulations {message.author.mention} you\'ve leveled up! Your new Level is **{level}**.')

            xpCollection.update_one({"UserId":f"{user_id}"}, {
                 "$set":{"Xp":newXp,"Level": level}
                 })

            asyncio.create_task(remove_from_cooldown(user_id, cooldown_duration))

        else:
            xpAdd = round(random.random() * (maxXP - minXP)) + minXP
            record = {  
                        "UserId": f"{user_id}",
                        "Xp": xpAdd,
                        "Level": 1,
                        "ShortName": message.author.name,
                        "lb": "all"
                    }
            xpCollection.insert_one(record)

async def QuickOrFeedbackCommands(message):
# Extract the command name and arguments
            command_parts = message.content[len("!"):].split()
            cmd = command_parts[0]
            args = ' '.join(command_parts[1:])

            # Look up the command in the database 
            custom_command_data =  quickCommandsCollection.find_one({"commandName": cmd})
            if custom_command_data:
                 quick = custom_command_data["commandRespond"]
                 return await message.channel.send(quick)
            
            # Find custom feedback command data 
            custom_feedback_command_data =  feedbackCommandsCollection.find_one({"commandName": cmd})

            if custom_feedback_command_data:
                role = message.guild.get_role(custom_feedback_command_data["roleThatCanUse"])
                if (has_role(AIRole)):
                    if(role is None):
                        channel_to_post_to = message.guild.get_channel(int(custom_feedback_command_data["channelID"]))

                        if channel_to_post_to is None:
                            return await message.reply("Channel doesn't exist!")
                        if message.attachments:        
                            attachments = []                    
                            for attachment in message.attachments:
                                    attachment = await attachment.to_file()
                                    attachments.append(attachment)           
                                
                            msg = await channel_to_post_to.send(f"**Author:** {message.author.mention}\n**Info:** {args}",
                                    files= attachments
                                    )
                            for button in buttons:
                                await msg.add_reaction(button)
                        else:
                            if not cmd:
                                return await message.reply("You need to write something!")

                            msg = await channel_to_post_to.send(f"**Author:** {message.author.mention}\n**Info:** {args}")
                            for button in buttons:
                                    await msg.add_reaction(button)

                            
                        await message.delete()
                   
                    elif(not role in message.author.roles):
                         return await message.reply("You can't use this command")
                        


###### OTHER FUNCTIONS #######
async def remove_from_cooldown(user_id, cooldown_duration):
    await asyncio.sleep(cooldown_duration)
    del user_cooldowns[user_id]

async def check_if_user_has_level_role(message,data_level):
    cs_role = message.guild.get_role(713692113082253323)
    as_role = message.guild.get_role(711705696709771267)
    bs_role = message.guild.get_role(711706071991058462)
    gs_role = message.guild.get_role(711705811633832009)
    gods_role = message.guild.get_role(717372676796317718)

    # You can get the member object from the message author
    member = message.author
    # Replace data.Level with the actual way to get the user's level
    
    if data_level >= cs_level and not cs_role in member.roles:
        await member.add_roles(cs_role)

    if data_level >= as_level and not as_role in member.roles:
        await member.add_roles(as_role)

    if data_level >= bs_level and not bs_role in member.roles:
        await member.add_roles(bs_role)

    if data_level >= gs_level and not gs_role in member.roles:
        await member.add_roles(gs_role)

    if data_level >= gods_level and not gods_role in member.roles:
        await member.add_roles(gods_role)

async def setup(bot):
    await bot.add_cog(messageEvents(bot))