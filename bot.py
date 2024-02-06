import requests
import pandas as pd
import sqlite3
from zipfile import ZipFile
from datetime import datetime, timedelta, date
from pyhelpers.ops import is_downloadable
import os
import sys
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

characters = {
        "banjokazooie": "<:banjokazooie:1128878890899746877>",
        "bayonetta": "<:bayonetta:1128878893043032124>",
        "bowser": "<:bowser:1128878894301315103>",
        "bowserjr": "<:bowserjr:1128878895853207712>",
        "byleth": "<:byleth:1128878898323652700>",
        "captainfalcon": "<:captainfalcon:1128878899791659089>",
        "chrom": "<:chrom:1128878901192577135>",
        "cloud": "<:cloudstrife:1128878902929014914>",
        "corrin": "<:corrin:1128878904925503559>",
        "daisy": "<:daisy:1128878907886669824>",
        "darkpit": "<:darkpit:1128878908796829847>",
        "darksamus": "<:darksamus:1128879499862343852>",
        "diddykong": "<:diddykong:1128879497417064499>",
        "donkeykong": "<:donkeykong:1128878912655593592>",
        "drmario": "<:drmario:1128879566342066226>",
        "duckhunt": "<:duckhunt:1128879568661520474>",
        "falco": "<:falco:1128878916904431656>",
        "fox": "<:foxmccloud:1128879603222585454>",
        "ganondorf": "<:ganondorf:1128879605307166720>",
        "greninja": "<:greninja:1128878919253246042>",
        "hero": "<:hero:1128879607421083678>",
        "iceclimbers": "<:iceclimbers:1128879609132372069>",
        "ike": "<:ike:1128879601230303332>",
        "incineroar": "<:incineroar:1128878922650636299>",
        "inkling": "<:inkling:1128879910178537483>",
        "isabelle": "<:isabelle:1128879912024027269>",
        "jigglypuff": "<:jigglypuff:1128878927398567946>",
        "joker": "<:joker:1128878929248260157>",
        "kazuya": "<:kazuya:1128879913894695032>",
        "ken": "<:ken:1128879915522076795>",
        "kingdedede": "<:kingdedede:1128894054768332911>",
        "kingkrool": "<:kingkrool:1128878935304843394>",
        "kirby": "<:kirby:1128878936550559744>",
        "link": "<:linkloz:1128893992013148241>",
        "littlemac": "<:littlemac:1128893995863519242>",
        "lucario": "<:lucario:1128893998828888084>",
        "lucas": "<:lucas:1128878940094742579>",
        "lucina": "<:lucina:1128894002272403617>",
        "luigi": "<:luigi:1128894005057433630>",
        "mario": "<:mario:1128899165972336800>",
        "marth": "<:marth:1128878943617949838>",
        "megaman": "<:megaman:1128899167406792734>",
        "metaknight": "<:metaknight:1128894017531301979>",
        "mewtwo": "<:mewtwo:1128878947115999262>",
        "miibrawler": "<:miibrawler:1128894020828020767>",
        "miigunner": "<:miigunner:1128894025110397018>",
        "miiswordfighter": "<:miiswordfighter:1128894028243533874>",
        "minmin": "<:minmin:1128878952014938193>",
        "mrgameandwatch": "<:mrgameandwatch:1128878954049191977>",
        "ness": "<:ness:1128894101484482630>",
        "olimar": "<:olimar:1128894105477464104>",
        "pacman": "<:pacman:1128894108749004851>",
        "palutena": "<:palutena:1128894114491023432>",
        "pichu": "<:pichu:1128894051496775780>",
        "pikachu": "<:pikachu:1128894056072753162>",
        "piranhaplant": "<:piranhaplant:1128899169256472576>",
        "pit": "<:pit:1128878961066258503>",
        "peach": "<:princesspeach:1128878957383667732>",
        "pokemontrainer": "<:pokemontrainer:1128916808469074010>", #
        "pyra": "<:pyra:1128916810633326595>", #
        "richter": "<:richter:1128894072468291756>",
        "ridley": "<:ridley:1128878964648198216>",
        "rob": "<:rob:1128894077446922282>",
        "robin": "<:robin:1128878969299677234>",
        "rosalina": "<:rosalina:1128878970956435538>",
        "roy": "<:roy:1128893993908977765>",
        "ryu": "<:ryu:1128893997125992508>",
        "samus": "<:samus:1128894001009926294>",
        "sephiroth": "<:sephiroth:1128894004096942100>",
        "sheik": "<:sheik:1128878976803295402>",
        "shulk": "<:shulk:1128878979005300836>",
        "simon": "<:simon:1128894006290567179>",
        "snake": "<:solidsnake:1128894011055284324>",
        "sonic": "<:sonic:1128894016432382002>",
        "sora": "<:sora:1128878982176190544>",
        "steve": "<:steve:1128916811883237426>", #
        "terry": "<:terry:1128894113165627392>",
        "toonlink": "<:toonlink:1128878985384837140>",
        "villager": "<:villager:1128916813221216257>", #
        "wario": "<:wario:1128894031401844827>",
        "wiifittrainer": "<:wiifittrainer:1128878988765446245>",
        "wolf": "<:wolfodonnell:1128894035386433606>",
        "yoshi": "<:yoshi:1128894039211655249>",
        "younglink": "<:younglink:1128878993815388190>",
        "zelda": "<:zelda:1128878996357120010>",
        "zerosuitsamus": "<:zerosuitsamus:1128879907485786253>"
    }

def correct(s):
    x = s
    return (x.replace(" ", "").replace("&", "and").replace("-","").replace(".","")).lower()
    

#https://github.com/smashdata/ThePlayerDatabase/releases/download/v2023.07.09/ultimate_player_database.zip

def calculate(new_file=None):
    print("searching for file...")

    most_recent = date.today()

    datestr = str(most_recent.strftime("v%Y.%m.%d"))
    url = "https://github.com/smashdata/ThePlayerDatabase/releases/download/" + datestr + "/ultimate_player_database.zip"

    r = None

    if new_file is None:
        r = requests.get(url, allow_redirects=True)
        while r.status_code != 200:
            most_recent = most_recent - timedelta(days=1)
            datestr = str(most_recent.strftime("v%Y.%m.%d"))
            url = "https://github.com/smashdata/ThePlayerDatabase/releases/download/" + datestr + "/ultimate_player_database.zip"
            r = requests.get(url, allow_redirects=True)
    else:
        r = new_file
        

    open('smashdata.zip', 'wb').write(r.content)

    print("URL is",url)

    print("extracting file...")

    with ZipFile("smashdata.zip",'r') as obj:
        obj.extractall()

    tiers = {"S":[], "A":[], "B":[], "C":[], "D":[], "E":[], "F":[]}
    best_mus = {}
    worst_mus = {}
    character_winrates = {}
    character_mus = {}
    character_games_recorded = {}

    print("calculating matchup charts and tier lists...")

    for character in characters:

        char_str = character

        print("character:", character)

        winrates = {}

        mus = { "-3": [], "-2": [], "-1": [], "0": [], "+1": [], "+2": [], "+3": []}
        
        con = sqlite3.connect("ultimate_player_database/ultimate_player_database.db")
            
        df = pd.read_sql_query("SELECT game_data FROM sets WHERE instr(game_data, '" + character + "') > 0", con)
            
        wins = {}
        total_games = {}
            
        mu_score = 0
        counter = 0
            
        for index, row in df.iterrows():
            s = row['game_data']
            s = s[1:len(s)-1]
            s = s.replace("{", "")
            s = s.replace("ultimate/", "")
            s = s.replace('"', "")
            games = s.split("}, ")
            for game in games:
                loser_char = game[game.find(" ",game.find("loser_char:"))+1:game.find(",",game.find("loser_char:"))]
                winner_char = game[game.find(" ",game.find("winner_char:"))+1:game.find(",",game.find("winner_char:"))]
                if (winner_char == character or loser_char == character) and (winner_char != loser_char): #prevent ditto matches from being recorded since that's nonsense...
                    #print("Winner:",winner_char)
                    #print("Loser:",loser_char)
                    #print()
                    if winner_char == character: # record a win for g&w
                        if loser_char not in total_games:
                            total_games[loser_char] = 1
                            wins[loser_char] = 1
                        else:
                            total_games[loser_char] += 1
                            wins[loser_char] += 1
                    else: # record a game played, but not a win
                        if winner_char not in total_games:
                            total_games[winner_char] = 1
                            wins[winner_char] = 0
                        else:
                            total_games[winner_char] += 1
                            
        con.close()

        character_games_recorded[character] = (total_games,wins)
            
        for key in wins:
            if key == "null" or key == "random":
                continue
            counter+=1
            mu_percent = wins[key]/total_games[key]
            winrates[key] = mu_percent
            if mu_percent > 0.49 and mu_percent < 0.51:
                mu_score+=0
                mus["0"].append(key)
            elif mu_percent >= 0.51 and mu_percent <= 0.6:
                mu_score+=1
                mus["+1"].append(key)
            elif mu_percent > 0.6 and mu_percent <= 0.7:
                mu_score+=2
                mus["+2"].append(key)
            elif mu_percent > 0.7:
                mu_score+=3
                mus["+3"].append(key)
            elif (1-mu_percent) >= 0.51 and (1-mu_percent) <= 0.6:
                mu_score-=1
                mus["-1"].append(key)
            elif (1-mu_percent) > 0.6 and (1-mu_percent) <= 0.7:
                mu_score-=2
                mus["-2"].append(key)
            elif (1-mu_percent) > 0.7:
                mu_score-=3
                mus["-3"].append(key)

        character_mus[character] = mus
        character_winrates[character] = winrates
        
        best_win = max(winrates.values())
        best_char = list(winrates.keys())[list(winrates.values()).index(best_win)]

        best_mus[character] = (best_char, best_win)
        
        worst_win = min(winrates.values())
        worst_char = list(winrates.keys())[list(winrates.values()).index(worst_win)]

        worst_mus[character] = (worst_char, worst_win)    

        mu_score = 1.0 * mu_score / counter
        charstr = (characters[character] + " ")

        if mu_score > 1:
            tiers["S"].append((characters[character], mu_score))
        elif mu_score < -1:
            tiers["F"].append((characters[character], mu_score))
        elif mu_score > 0.6 and mu_score <= 1:
            tiers["A"].append((characters[character], mu_score))
        elif mu_score > 0.2 and mu_score <= 0.6:
            tiers["B"].append((characters[character], mu_score))
        elif mu_score > -0.2 and mu_score <= 0.2:
            tiers["C"].append((characters[character], mu_score))
        elif mu_score > -0.6 and mu_score <= -0.2:
            tiers["D"].append((characters[character], mu_score))
        elif mu_score >= -1 and mu_score <= -0.6:
            tiers["E"].append((characters[character], mu_score))

        for tier in tiers:
            l = len(tiers[tier])
            for i in range(0,l):
                for j in range(0,l-i-1):
                    if (tiers[tier])[j][1] < (tiers[tier])[j+1][1]:
                        temp = (tiers[tier])[j]
                        (tiers[tier])[j] = (tiers[tier])[j+1]
                        (tiers[tier])[j+1] = temp

    return (tiers, character_mus, character_games_recorded, best_mus, worst_mus, most_recent, url, character_winrates)


load_dotenv()
client = commands.Bot(command_prefix="rob!",intents=discord.Intents.all())
TOKEN = os.getenv('DISCORD_TOKEN')

initial_calculations = calculate()

tiers = initial_calculations[0]
character_mus = initial_calculations[1]
character_games_recorded = initial_calculations[2]
best_mus = initial_calculations[3]
worst_mus = initial_calculations[4]
most_recent = initial_calculations[5]
url = initial_calculations[6]
character_winrates = initial_calculations[7]

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))
    update.start()

@client.command(name = 'mu_chart', brief='Displays the matchup chart.', description='Displays the matchup chart.')
async def mu_chart(ctx, arg=""):
    print("Matchup chart requested.")
    arg = correct(arg)
    if arg=="" or arg not in characters:
        await ctx.send("ERROR: Invalid argument. Type rob!chars for a list of accepted arguments.")
    elif character_mus is None or best_mus is None or worst_mus is None:
        await ctx.send("ERROR: Matchup chart is currently being calculated. Try again later.")
    else:
        s = ""
        time_str = most_recent.strftime("%B %d, %Y")
        titl="Matchup chart for " + characters[arg] + " based on data from " + time_str
        mus = character_mus[arg]
        chars_used = 0
        for i in mus:
            if len(mus[i]) == 0:
                continue
            s+=(i+": ")
            for char in mus[i]:
                s += (characters[char] + " ")
            s+="\n"
        embed=discord.Embed(title=titl,description=s)
        best = characters[best_mus[arg][0]] + " (Win Rate: %.2f percent)" % (best_mus[arg][1] * 100)
        embed.add_field(name="Best Matchup",value=best,inline=False)
        worst = characters[worst_mus[arg][0]] + " (Win Rate: %.2f percent)" % (worst_mus[arg][1] * 100)
        embed.add_field(name="Worst Matchup",value=worst,inline=False)
        await ctx.send(embed=embed)
        

@client.command(name = 'chars', brief='Displays all characters.', description='Displays all characters.')
async def chars(ctx, arg=""):
    s = ""
    for i in characters:
        s += (i+", ")
    s = s[0:len(s)-1]
    await ctx.send(s)

@client.command(name = 'tier_list', brief='Calculates a tier list.', description='Calculates a tier list.')
async def tier_list(ctx):
    if tiers is None:
        await ctx.send("ERROR: Tier list is currently being calculated. Try again later.")
    else:
        s = ""
        time_str = most_recent.strftime("%B %d, %Y")
        titl="Tier list based on data from " + time_str + ":"
        for tier in tiers:
            if len(tiers[tier]) == 0:
                continue
            s += (tier+": ")
            for char in tiers[tier]:
                s += (char[0] + " ")
            s+="\n"
        embed=discord.Embed(title=titl,description=s)
        await ctx.send(embed=embed)

@client.command(name = 'matchup', brief='Shows a specific matchup.', description='Shows a specific matchup.')
async def matchup(ctx, *args):
    if len(args) != 2:
        await ctx.send("ERROR: Invalid argument amount. Provide only two arguments.")
    elif character_games_recorded is None:
        await ctx.send("ERROR: Data is currently being calculated. Try again later.")
    else:
        char_1 = correct(args[0])
        char_2 = correct(args[1])
        if char_1 not in characters or char_2 not in characters:
            await ctx.send("ERROR: Invalid argument. Type rob!chars for a list of accepted arguments.")
        elif char_1 == char_2:
            await ctx.send("ERROR: Duplicate arguments. Provide two distinct arguments.")
        else:
            s = ""
            titl = ("%s VS %s:" % (characters[char_1], characters[char_2]))
            embed=discord.Embed(title=titl,description="")
            total_games = (character_games_recorded[char_1][0][char_2])
            embed.add_field(name="Total Games Played", value=total_games, inline=False)
            wins_1 = (character_games_recorded[char_1][1][char_2])
            embed.add_field(name="Wins for %s" % characters[char_1], value=wins_1, inline=False)
            wins_2 = (character_games_recorded[char_2][1][char_1])
            embed.add_field(name="Wins for %s" % characters[char_2], value=wins_2, inline=False)
            winrate_1 = ((character_winrates[char_1][char_2]) * 100)
            embed.add_field(name="%s Win Rate" % characters[char_1], value = "%.2f percent" % winrate_1, inline=False)
            winrate_2 = ((character_winrates[char_2][char_1]) * 100)
            embed.add_field(name="%s Win Rate" % characters[char_2], value = "%.2f percent" % winrate_2, inline=False)
            await ctx.send(embed=embed)
            

@tasks.loop(seconds=1)
async def update():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("time:", current_time)
    if current_time == "00:00:00":
        today = date.today()
        new_datestr = str(today.strftime("v%Y.%m.%d"))
        new_url = "https://github.com/smashdata/ThePlayerDatabase/releases/download/" + new_datestr + "/ultimate_player_database.zip"
        r = requests.get(new_url, allow_redirects=True)
        while (new_url != url) and (r.status_code != 200):
            print("testing", new_datestr)
            today = today - timedelta(days=1)
            new_datestr = str(today.strftime("v%Y.%m.%d"))
            new_url = "https://github.com/smashdata/ThePlayerDatabase/releases/download/" + new_datestr + "/ultimate_player_database.zip"
            r = requests.get(new_url, allow_redirects=True)
        if new_url != url:
            print("update found!")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print("not yet...")

client.run(TOKEN)
