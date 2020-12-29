import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix='vc ', 
                    description='A voice channel bot created by Jason11ookJJ#3151', 
                    help_command=commands.DefaultHelpCommand(no_category = 'help'))
load_dotenv()
bot.owner_id = int(os.getenv("OWNER"))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vc help"))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(os.environ['TOKEN'])
