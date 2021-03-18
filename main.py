import os 
import sys 

import discord
from discord.ext import commands

import DiscordUtils

import sqlite3 
import json 


import colorama 
from colorama import init, Fore 
if os.name == "nt": # Windows users needs this option
    init(convert=True)

###################################

TOKEN = "Your bot token goes here"
PREFIX = "The prefix you want"

###################################

intents = discord.Intents.default()
intents.members = True
    
bot = commands.AutoShardedBot(command_prefix=PREFIX, intents=intents)
tracker = DiscordUtils.InviteTracker(bot)

###################################

@bot.event
async def on_ready():
    await tracker.cache_invites()
    print('Bot Ready')

@bot.event
async def on_invite_create(invite):
    await tracker.update_invite_cache(invite)

@bot.event
async def on_guild_join(guild):
    await tracker.update_guild_cache(guild)

@bot.event
async def on_invite_delete(invite):
    await tracker.remove_invite_cache(invite)

@bot.event
async def on_guild_remove(guild):
    await tracker.remove_guild_cache(guild)
    
@bot.command()
async def invites(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
         
    with open("main.json", "r") as enter:
        c = json.load(enter)
        
    try:
        invite = dict(c[str(ctx.guild.id)][str(member.id)])
    except KeyError:
        await ctx.send("This user doesn't have invites")
        return
    
    real = 0
    leaved = 0
    fake = 0 
    
    for value in invite.values():
        if value == "1":
            real += 1
        if value == "2":
            leaved += 1
        if value == "3":
            fake += 1
            
    embed = discord.Embed(
        title = f"{member.name}'s Invites",
        description = f"```\nReal: {real}\nLeaved: {leaved}\nFake: {fake}\n```"
    )
    
    await ctx.send(embed=embed)
            
    
@bot.event 
async def on_member_remove(member): 
    with open("main.json", "r") as enter:
        c = json.load(enter)
        
    
    for i in list(c.values()):
        i = list(i)[0]
        try:
            c[str(member.guild.id)][i][str(member.id)] = "2"
        except:
            pass 
        
    with open("main.json", "w") as out:
        json.dump(c, out, indent=4)
    

@bot.event
async def on_member_join(member):
    """
    CODE

    1: REAL
    2: LEAVED
    3: FAKE
    """
    inviter = await tracker.fetch_inviter(member)
    
    with open("main.json", "r") as enter:
        c = json.load(enter)

    try:
        user_invite = c[str(member.guild.id)][str(inviter.id)][str(member.id)]
        c[str(member.guild.id)][str(inviter.id)][str(member.id)] = "1"
        
        with open("main.json", "w") as out:
            json.dump(c, out, indent=4)
        return
        
    except Exception as e:
        try:
            a = c[str(member.guild.id)]
        except Exception as e:
            c[str(member.guild.id)] = {}
        try:
            a = c[str(member.guild.id)][str(inviter.id)]
        except Exception as e:
            c[str(member.guild.id)][str(inviter.id)] = {}
                
                
    c[str(member.guild.id)][str(inviter.id)][str(member.id)] = "1"   
                
        
    with open("main.json", "w") as out:
        json.dump(c, out, indent=4)

    
###################################
    
if __name__ == '__main__':
    bot.run(TOKEN)