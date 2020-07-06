import asyncio
import os
import discord
from discord.ext import commands
#import environment_variables

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

def is_mention(input):
	return input.startswith("<@!")



########################### BOOT ########################### 

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(activity=discord.Game(name="!intro [name or mention]"))



########################### COMMANDS ########################### 

@bot.command(name='intro', pass_context=True)
async def get_intro(ctx, *,  target_user):
	try:
		if is_mention(target_user):
			converter = commands.UserConverter()
			target_user = await converter.convert(ctx, target_user)
		else:
			target_user = await string_to_user(ctx, target_user) #target user can be a string
		await send_intro(ctx, target_user)
	except Exception as e:
		print(e)
		await ctx.channel.send(content="Could not fetch intro.")

async def get_intro(target_user):
	intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
	async for message in intro_channel.history(limit=300):
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
		#embed.add_field(image=target_user.avatar_url)
		await ctx.author.send(embed=embed)
	except Exception as e:
		print(e)
		await ctx.channel.send("Could not fetch intro.")

async def string_to_user(ctx, string_to_convert):
	string_to_convert = string_to_convert.lower()
	for member in ctx.guild.members:
		if string_to_convert == str(member.nick).lower() or string_to_convert == str(member.name).lower():
			return member



########################### OTHER STUFF ########################### 

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if message.author.id == bot.user.id:
			return

bot.run(os.environ["BOT_TOKEN"])