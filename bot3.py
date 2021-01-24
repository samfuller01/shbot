# bot.py
import os

import discord
from dotenv import load_dotenv
from Game import Game

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

client = discord.Client(intents=intents)
global game_id
game_id = 1
games = []
global monty
monty = None

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        #print(guild.members)
        print(client.user, "connected to", guild.name, "!")

        global monty
        monty = guild.get_member(280471970406072320)
        
        await cleanup(guild)
        #print(guild.roles)
        print(guild.emojis)
        #g = Game()
        
        #for i in range(7)
        #g.add_player
        
        #g = Game()

async def cleanup(guild):
    c = [x for x in guild.channels if (x.name.startswith("game") or x.name.startswith("seat"))]
    for a in c:
        await a.delete()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global monty
    print(monty)
    print(message.author.id)

    if message.author == monty:
        if message.content == "clear":
            deleted = await message.channel.purge(limit=100)

        #for game in games:
        #    await game.handle_input(message)

        if message.content.startswith(".game"):
            players = []
            text = message.content
            while 1:
                start = text.find("<")
                end = text.find(">")
                if start < 0 or end < 0:
                    break
                player_id = text[start+3:end]
                #print("searching for", int(player_id))
                member = message.guild.get_member(int(player_id))
                players.append(member)
                print("found", member)
                text = text[end+1:]
            global game_id
            g = Game(message.guild, game_id, client)
            
            game_id += 1

            for p in players:
                g.add_player(p)
            games.append(g)
            
            await g.prepare_game()
            await g.start_game()
        
        if message.content == "cleanup":
            await cleanup(message.guild)

client.run(TOKEN)