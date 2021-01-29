import discord
import json

client = discord.Client()

@client.event
async def on_ready():

    guild = await client.fetch_guild(796953059938140180)
    channels = await guild.fetch_channels()

    for ch in channels:
        if ch.category == None:
            await ch.delete()

    exit()

# DO NOT RUN THIS SHIT, IT DELETES ALL CATEGORIES
# (THUS ORPHANING ALL CHANNELS) AND THEN GOES AND
# DELETES THOSE TOO.
