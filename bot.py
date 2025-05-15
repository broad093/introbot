from dotenv import load_dotenv
import os
import json
from os import path
import discord 
from discord.ext import commands

intents = discord.Intents.all()  # All but the two privileged ones
intents.members = True  # Subscribe to the Members intent
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

load_dotenv('.env')
# environment variables
INTRO_CHANNEL_ID = int(os.environ["INTRO_CHANNEL_ID"])
GUILD_ID = int(os.environ["GUILD_ID"])
BOT_TOKEN = os.environ["BOT_TOKEN"]

filename = './intros.json'
messagehistory = './history.json'
setIntros = {}
historyIntros = {}
 
# Clean this up later, this holds the JSON data. Adjust it so that it fetches data from JSON in the future.
if path.isfile(filename) is False:
  raise Exception("File not found")

if path.isfile(messagehistory) is False:
  raise Exception("File not found")
 
# Read JSON file
with open(filename) as fp:
  setIntros = json.load(fp)
with open(messagehistory) as fp:
  historyIntros = json.load(fp)
 
# Verify existing dict
print(type(setIntros))
print(type(historyIntros))
 

async def update_set_intros():
    with open(filename, 'w') as json_file:
        json.dump(setIntros, json_file, 
                            indent=4,  
                            separators=(',',': '))
    print('Successfully updated set intro')

def check_set_intro_list(target_user):
    while True:
        with open('./intros.json') as fp:
            data = json.load(fp)
        for user in data:
            if data[user]["ID"] == target_user.id:
                return True
        break

def check_intro_history_list(target_user):
    while True:
        with open('./history.json') as fp:
            data = json.load(fp)

        for user in data:
            if data[user]["ID"] == target_user.id:
                return True
        break

async def update_intro_list():
    global message_list
    intro_channel = guild.get_channel(INTRO_CHANNEL_ID)
    message_list = [message_list async for message_list in intro_channel.history(limit=10000,oldest_first=False)]

async def refresh_intro_list():
    for message in message_list:
        if message.type != "public_thread" or "private_thread":
            historyIntros[message.author.name] = {'ID':message.author.id,'Intro':message.id}
    
    with open(messagehistory, 'w') as json_file:
        json.dump(historyIntros, json_file, 
                            indent=4,  
                            separators=(',',': '))

########################### HELPERS ########################### 

def is_intro_channel(ctx):
    intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
    return ctx.channel == intro_channel

def is_botadmin(ctx):
    zach_id = 138458225958715392
    return ctx.author.id == zach_id

def is_admintea(ctx):
    tea_id = 800778750459379792
    return ctx.author.id == tea_id

def make_mention_object_by_id(author_id):
    return "<@{}>".format(author_id)

def strip_mention_to_id(target_user):
    return int(target_user.strip("<@").strip(">"))

def is_mention(input):
    return input.startswith("<@")

def is_messageURL(input):
    return input.startswith("https://discord.com/channels/{}").format(INTRO_CHANNEL_ID)

def is_messageID(input):
    return int(input)

async def fileify(avatar_url):
    filename = "useravatar.jpg"
    await avatar_url.save(filename)
    file = discord.File(fp=filename)
    return file

async def make_embed(target_user):
    if check_set_intro_list(target_user):
        username, message, url = await get_setintro(target_user)
    elif check_intro_history_list(target_user):
        username, message, url = await get_intro(target_user)

# adjusted it so that the 1024 character limit is now 4096
# embed color pulls from user's role color
# added link to original message
    embed = discord.Embed(title="**{}**".format(username),description="**Intro**\n{}".format(message),color=target_user.color)
    embed.set_thumbnail(url=target_user.avatar)
    embed.add_field(name="--", value="[*View original message...*]({})".format(url), inline=False)
    return embed

########################### BOOT ########################### 

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity=discord.Game(name="!intro [name or mention]"))

    #imagine a world where I didn't have to do this
    #but this has to work on ready so here we are
    global guild
    guild = bot.get_guild(GUILD_ID)

    print('Loading introductions list...')
    await update_intro_list()
    await refresh_intro_list()
    print('history.json updated and refreshed')
    print('------')

########################### COMMANDS ########################### 
# @client.group(invoke_without_command = True) # for this main command (.help)
# async def help(ctx):
#     await ctx.send("Help! Categories : Moderation, Utils, Fun")

# @help.command()   #For this command (.help Moderation)
# async def Moderation(ctx):
#     await ctx.send("Moderation commands : kick, ban, mute, unban")

@bot.group(invoke_without_command=True)
async def intro(ctx, *,target_user):
    if is_intro_channel(ctx):
        return
    else:
        try:
            print("encoding", target_user)
            if is_mention(target_user):
                target_user = await guild.fetch_member(strip_mention_to_id(target_user))
                print("I tried converting user", target_user)
            else:
                target_user = await string_to_user(target_user) #target user can be a string
            await send_intro(ctx, target_user)
        except Exception as e:
            print(e)
            await ctx.channel.send(content="Could not fetch intro.")

@intro.command(name="-set")
async def set(ctx, link: commands.MessageConverter):
    print("setting intro...")
    if is_intro_channel(ctx):
        return
    else:
        try:
            if ctx.author.id == link.author.id:
                setIntros[ctx.author.name] = {'ID':link.author.id,'Intro':link.id}
                await update_set_intros()
                print("I tried setting user", link.author)
                await ctx.channel.send(f"Updated intro to: {link.jump_url}")
            else:
                print("I tried setting user", ctx.author, "intro as", link.author)
                await ctx.channel.send(content="Please set your own intro.")
        except Exception as e:
            print(e, "\ninvalid link")
            await ctx.channel.send(content="Please set a valid intro link.")
@set.error
async def set_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        print("invalid intro link")
        await ctx.channel.send(content="Please set a valid intro link.")

@intro.command(name="-reset")
async def reset(ctx: commands.MessageConverter):
    print("resetting to default intro...")
    if is_intro_channel(ctx):
        return
    else:
        try:
            if ctx.author.name in setIntros:
                setIntros.pop(ctx.author.name)
                await update_set_intros()
                print("I tried resetting intro by", ctx.author.name)
                await ctx.channel.send(f"Reset to default intro.")
        except Exception as e:
            print(e, "\nUser not in setIntros")
            await ctx.channel.send(content="Unable to reset intro, no saved intro found.")

@intro.command(name="-dm")
async def dm(ctx, *,  target_user):
    print("get_intro_dm",target_user)
    try:
        if is_mention(target_user):
            target_user = await guild.fetch_member(strip_mention_to_id(target_user))
            print("I tried converting user for DM", target_user)
        else:
            target_user = await string_to_user(target_user) #target user can be a string
        await send_intro_by_dm(ctx, target_user)
    except Exception as e:
        print(e)
        if is_intro_channel(ctx):
            await ctx.channel.send(content="Could not fetch intro.")

@intro.command(name="-refresh")
async def refresh(ctx):
    print("refreshing intro list")
    if is_intro_channel(ctx):
        return
    else:
        await refresh_intro_list()
        await ctx.channel.send(content="Refreshed intro list.")

########################### HELP ############################## 
@intro.command(name="-help")
async def help(msg):
    user = msg.author.id

    if user == bot.user.id:
        return

    embed = discord.Embed(title='Help',description=
    """
Someone asks a question and you'd like some quick insight on their background? Use introbot to help! This bot pulls a user's first message from the introductions channel.

**NOTE: If you would like to change your introduction, you must edit your *first original* message in <#1030656443386445864> or use `!intro -set URL` to pull a new message.**

**ー　COMMANDS　ー**
**!intro**
*Use this command followed by the user's name or handle to pull a user's introduction.
You can either mention the user or type their EXACT name as known in the sever.*
・EXAMPLE 1: `!intro @BobaTalks`
・EXAMPLE 2: `!intro BobaTalks`

**!intro -set *URL* **
*Use this command to set an introduction. Must be __your own__ message written in the introductions channel.*
・EXAMPLE: `!intro -set https://discord.com/channels/10299..../..`

**!intro -reset **
*Use this command to reset your introduction to your first message sent in the introductions channel.*
・EXAMPLE: `!intro -reset`

Type `!intro -help` for more information on a command.
...
    """,
    color=0xcda971)
    embed.set_footer(text="If there are any problems with this bot, please let a moderator know.")
    await msg.send(embed=embed)

    print('help information sent')
# - - - - - - - - - - - - - - - - - -

async def get_setintro(target_user):
    intro_channel = guild.get_channel(INTRO_CHANNEL_ID)
    with open('./intros.json') as fp:
        data = json.load(fp)
    for user in data:
        if data[user]["ID"] == target_user.id:
            messageObj = await intro_channel.fetch_message(data[user]["Intro"])
            print("sending set intro")
            return messageObj.author.display_name, messageObj.content, messageObj.jump_url

async def get_intro(target_user):
    intro_channel = guild.get_channel(INTRO_CHANNEL_ID)
    with open('./history.json') as fp:
        data = json.load(fp)
    for user in data:
        if data[user]["ID"] == target_user.id:
            print("sending saved intro")
            obj = await intro_channel.fetch_message(data[user]["Intro"])
            return obj.author.display_name, obj.content, obj.jump_url

async def send_intro_by_dm(ctx, target_user):
    print("send_intro_dm",target_user)
    try:
        embed = await make_embed(target_user)
        await ctx.author.send(embed=embed)
    #probably too long for embed
    except discord.errors.HTTPException as e:
        print(e)
        username, message, url = await get_intro(target_user)
        introstring = "**{}**\n---------------------------------------\n".format(username)
        introstring += "{}\n---------------------------------------".format(message)
        avatar_file = await fileify(target_user.avatar)
        await ctx.author.send(content=introstring, file=avatar_file)
    except Exception as e:
        print(e)
        await ctx.channel.send("Could not fetch intro.")

async def send_intro(ctx, target_user):
    print("send_intro",target_user)
    try:
        embed = await make_embed(target_user)
        await ctx.channel.send(embed=embed)
    #probably too long for embed
    except discord.errors.HTTPException as e:
        print(e)
        username, message, url = await get_intro(target_user)
        introstring = "**{}**\n---------------------------------------\n".format(username)
        introstring += "{}\n---------------------------------------".format(message)
        avatar_file = await fileify(target_user.avatar)
        await ctx.channel.send(content=introstring, file=avatar_file)
    except Exception as e:
        print(e)
        await ctx.channel.send("Could not fetch intro.")

async def string_to_user(string_to_convert):
    string_to_convert = string_to_convert.lower()
    for member in guild.members:
        if string_to_convert == str(member.display_name).lower() or string_to_convert == str(member.name).lower():
            return member

########################### CHANGES ############################## 
@bot.command(name='changelog', pass_context=True)
async def help_info(msg):
    user = msg.author.id

    if user == bot.user.id:
        return

    embed = discord.Embed(title='Changelog',color=0xcda971)
    embed.add_field(name="**introbot (v2.1, beta) - updated 04.20.2024**",
    value=
    """
➢ General bug fixes related to discord updates
➢ Adjusted intro refresh to happen everytime a new message is sent in introductions instead of every minute
➢ Added new command to reset intro to first message (!intro -reset)

Type `!intro -help` for more information on specific commands.
...
    """,inline=False)
    embed.set_footer(text="If there are any problems with this bot, please let a moderator know.")
    await msg.send(embed=embed)

    print('changelog sent')

########################### OTHER STUFF ########################### 

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    # if message is sent in channel then add new intro to json
    if is_intro_channel(message):
        if message.type != "public_thread" or "private_thread":
            await update_intro_list()
            await refresh_intro_list()
        print('Introductions updated and refreshed')

    if message.author.id == bot.user.id:
        return

#### RENDER PORT BINDING ####
# Render requires a web server to keep the bot alive on the free tier.
from flask import Flask
import threading

# Create Flask app
app = Flask("")

@app.route("/")
def home():
    return "Bot is running"

def run_webserver():
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT or default 10000
    app.run(host="0.0.0.0", port=port)

# Start the Flask web server in a separate thread so it doesn't block your bot
threading.Thread(target=run_webserver).start()

# Start bot
bot.run(BOT_TOKEN)
