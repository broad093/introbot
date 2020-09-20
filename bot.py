import asyncio
import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
INTRO_CHANNEL_ID = int(os.environ["INTRO_CHANNEL_ID"])
GUILD_ID = int(os.environ["GUILD_ID"])

########################### HELPERS ########################### 

def is_intro_channel(ctx):
	intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
	return ctx.channel == intro_channel

def is_botadmin(ctx):
	zach_id = 138458225958715392
	return ctx.author.id == zach_id

def make_mention_object_by_id(author_id):
	return "<@{}>".format(author_id)

def is_mention(input):
	return input.startswith("<@!")

async def fileify(avatar_url):
	filename = "avatar.jpg"
	await avatar_url.save(filename)
	file = discord.File(fp=filename)
	return file


########################### BOOT ########################### 

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(activity=discord.Game(name="!intro [name or mention]"))

	#imagine a world where I didn't have to do this
	#but this has to work on ready so here we are
	global guild
	guild = bot.get_guild(GUILD_ID)


########################### COMMANDS ########################### 

@bot.command(name='intro', pass_context=True)
async def get_intro(ctx, *,  target_user):
	try:
		if is_mention(target_user):
			converter = commands.UserConverter()
			target_user = await converter.convert(ctx, target_user)
		else:
			target_user = await string_to_user(target_user) #target user can be a string
		await send_intro(ctx, target_user)
	except Exception as e:
		print(e)
		await ctx.channel.send(content="Could not fetch intro.")

async def get_intro(target_user):
	intro_channel = guild.get_channel(INTRO_CHANNEL_ID)
	message_list = await intro_channel.history(limit=500).flatten()
	message_list_reversed = message_list.reverse()

	for message in message_list_reversed:
		if message.author == target_user:
			if target_user.nick:
				return target_user.nick, message.content
			else:
				return target_user.name, message.content

async def send_intro(ctx, target_user):
	try:
		username, message = await get_intro(target_user)
		embed = discord.Embed(title="**{}**".format(username), color=0x7598ff)
		embed.set_thumbnail(url=target_user.avatar_url)
		embed.add_field(name="Intro", value=message, inline=False)
		await ctx.author.send(embed=embed)
	#probably too long for embed
	except discord.errors.HTTPException as e:
		print(e)
		username, message = await get_intro(target_user)
		introstring = "**{}**\n---------------------------------------\n".format(username)
		introstring += "{}\n---------------------------------------".format(message)
		avatar_file = await fileify(target_user.avatar_url)
		await ctx.author.send(content=introstring, file=avatar_file)
	except Exception as e:
		print(e)
		await ctx.channel.send("Could not fetch intro.")

async def string_to_user(string_to_convert):
	string_to_convert = string_to_convert.lower()
	for member in guild.members:
		if string_to_convert == str(member.nick).lower() or string_to_convert == str(member.name).lower():
			return member



########################### OTHER STUFF ########################### 

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	#dont talk to urself bruh
	if message.author.id == bot.user.id:
			return

bot.run(os.environ["BOT_TOKEN"])
