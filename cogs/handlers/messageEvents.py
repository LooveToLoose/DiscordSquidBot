from discord.ext import commands
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import os

db = MongoClient(os.getenv("MONGO_DB_URI"), server_api=ServerApi('1'))["test"]
yoCollection = db["yos"]
quickCommandsCollection = db["quick commands"]
feedbackCommandsCollection = db["feedback commands"]


AIRole = int(os.getenv("AIRole"))
prefixes = "!"
buttons = ["<:Diff1InfinitelyEasy:686910602689380422>",
           "<:Down:946437519476666379>"]

class messageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        if message.author.bot:
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

#### MAIN HANDLERS #####

async def yoSystem_Handler(message):
        yo_variations = ["yo", "Yo!", "yoy", "yoyo","<:YO:714280062437818559>","oy","<:yonas:741360791667605596>", "<:YoBoss:787408970792697876>", "<:SquidYo:714937825518157905>","<:shellyo:741359253050097674>"]

        #check if message contains words in
        content = message.content.lower()
        if any(variation in content for variation in yo_variations):
            yoCollection.find_one_and_update({"word":"yo"}, {"$inc":{"yo": 1}})

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
                if False: # TODO: Fix this check, or possibly remove feedback commands in general? Gotta ask.
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

async def setup(bot):
    await bot.add_cog(messageEvents(bot))
