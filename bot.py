import asyncio
import os
import discord
from discord.ext import commands
import environment_variables

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
INTRO_CHANNEL_ID = int(os.environ["INTRO_CHANNEL_ID"])

########################### HELPERS ########################### 

def is_intro_channel(ctx):
	intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
	return ctx.channel == intro_channel

def is_botadmin(ctx):
	zach_id = 138458225958715392
	return ctx.author.id == zach_id

def make_mention_object_by_id(author_id):
	return "<@{}>".format(author_id)



########################### BOOT ########################### 

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')



########################### COMMANDS ########################### 

@bot.command(name='intro', pass_context=True)
async def get_intro(ctx, target_user):
	try:
		converter = commands.UserConverter()
		target_user = await converter.convert(ctx, target_user)
		await send_intro(ctx.author, target_user)
	except Exception as e:
		print(e)
		await ctx.channel.send(content="Could not fetch intro.")

async def get_intro(target_user):
	intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
	async for message in intro_channel.history(limit=200):
		if message.author == target_user:
			return target_user.name, message.content

async def send_intro(ctx_user, target_user):
	username, message = await get_intro(target_user)
	dm_message_content = "**{}**. \n--------------------------------------\n{}\n--------------------------------------".format(username, message)
	await ctx_user.send(dm_message_content)

async def string_to_user(string_to_convert):
	for user in all_users:
		if string_to_convert == user.nick or string_to_convert == user.name:
			return user



########################### OTHER STUFF ########################### 

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if message.author.id == bot.user.id:
			return

bot.run(os.environ["BOT_TOKEN"])