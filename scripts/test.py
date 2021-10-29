import requests

from LoLCoaching.config import config
import utils

# RIOT API Related informations
base_url_euw = "https://euw1.api.riotgames.com"
base_url_europe = "https://europe.api.riotgames.com"
game = "lol"
summoner_api = "summoner/v4/summoners"
match_api = "match/v5/matches"
by_name = "by-name"
by_puuid = "by-puuid"

# Put the username of the player you want to see the stats.
# ingame_position is TOP, JUNGLE, MIDDLE, BOTTOM or UTILITY
username = "azertgab"
ingame_position = "MIDDLE"

# Getting RIOT API key defined in config.ini
api_key = config.get_api_key()

# Getting player puuid to retrieve games.
url = f"{base_url_euw}/{game}/{summoner_api}/{by_name}/{username}?api_key={api_key}"
resp = requests.get(url)
data = resp.json()
puuid = data["puuid"]

# Getting last 50 games played by player.
url = f"{base_url_europe}/{game}/{match_api}/{by_puuid}/{puuid}/ids?start=0&count=50&api_key={api_key}"
resp = requests.get(url)
match_list = resp.json()

# Total stats
position_match_count = 0
average_damage_share = 0
average_gold_share = 0
average_gold_efficiency = 0

# Stats in wins
win_number = 0
win_average_damage_share = 0
win_average_gold_share = 0
win_average_gold_efficiency = 0

# Stats in losses
lose_number = 0
lose_average_damage_share = 0
lose_average_gold_share = 0
lose_average_gold_efficiency = 0

# championList is a dictionary of all champions played at given position with detailed stats for the champion.
championList = {}

# valid_match_list is a list of all match were the player played in given position.
valid_match_list = []

for match in match_list:
    url = f"{base_url_europe}/{game}/{match_api}/{match}?api_key={api_key}"
    resp = requests.get(url)
    data_json = resp.json()
    if "info" not in data_json:
        continue
    data = data_json["info"]
    win = False
    if data["mapId"] == 11 and data["gameMode"] == "CLASSIC" and data["gameType"] == "MATCHED_GAME":
        team_1_damage = 0
        team_2_damage = 0
        team_1_gold = 0
        team_2_gold = 0

        # Calculating total damage and gold of the team
        for player in data["participants"]:
            if player["teamId"] == 100:
                team_1_damage += player["totalDamageDealtToChampions"]
                team_1_gold += player["goldEarned"]
            if player["teamId"] == 200:
                team_2_damage += player["totalDamageDealtToChampions"]
                team_2_gold += player["goldEarned"]

        # Getting player specific information
        for player in data["participants"]:
            if player["summonerName"] == username and player["teamPosition"] == ingame_position:
                # Save that specific match so we can get the timeline details about it.
                valid_match_list.append(match)

                # If champion is not in championList, we set all values to get the list ready.
                if player["championName"] not in championList:
                    championList[player["championName"]] = {}
                    championList[player["championName"]]["championName"] = player["championName"]
                    championList[player["championName"]]["gameCount"] = 0
                    championList[player["championName"]]["wins"] = 0
                    championList[player["championName"]]["losses"] = 0
                    championList[player["championName"]]["damageShare"] = 0
                    championList[player["championName"]]["goldShare"] = 0
                    championList[player["championName"]]["goldEfficiency"] = 0
                    championList[player["championName"]]["winDamageShare"] = 0
                    championList[player["championName"]]["winGoldShare"] = 0
                    championList[player["championName"]]["winGoldEfficiency"] = 0
                    championList[player["championName"]]["lossDamageShare"] = 0
                    championList[player["championName"]]["lossGoldShare"] = 0
                    championList[player["championName"]]["lossGoldEfficiency"] = 0

                # Calculate share of gold, damage, and gold efficiency.
                game_damage_share = 0
                game_gold_share = 0
                game_gold_efficiency = player["totalDamageDealtToChampions"] / player["goldEarned"] * 100
                if player["teamId"] == 100:
                    game_damage_share = player["totalDamageDealtToChampions"] / team_1_damage * 100
                    game_gold_share = player["goldEarned"] / team_1_gold * 100
                if player["teamId"] == 200:
                    game_damage_share = player["totalDamageDealtToChampions"] / team_2_damage * 100
                    game_gold_share = player["goldEarned"] / team_2_gold * 100

                # Add overall stats
                average_damage_share += game_damage_share
                average_gold_share += game_gold_share
                average_gold_efficiency += game_gold_efficiency
                position_match_count += 1
                if player["win"] is True:
                    win_average_damage_share += game_damage_share
                    win_average_gold_share += game_gold_share
                    win_average_gold_efficiency += game_gold_efficiency
                    win_number += 1
                else:
                    lose_average_damage_share += game_damage_share
                    lose_average_gold_share += game_gold_share
                    lose_average_gold_efficiency += game_gold_efficiency
                    lose_number += 1

                # Add champion specific stats
                championList[player["championName"]]["gameCount"] += 1
                championList[player["championName"]]["damageShare"] += game_damage_share
                championList[player["championName"]]["goldShare"] += game_gold_share
                championList[player["championName"]]["goldEfficiency"] += game_gold_efficiency
                if player["win"] is True:
                    championList[player["championName"]]["wins"] += 1
                    championList[player["championName"]]["winDamageShare"] += game_damage_share
                    championList[player["championName"]]["winGoldShare"] += game_gold_share
                    championList[player["championName"]]["winGoldEfficiency"] += game_gold_efficiency
                else:
                    championList[player["championName"]]["losses"] += 1
                    championList[player["championName"]]["lossDamageShare"] += game_damage_share
                    championList[player["championName"]]["lossGoldShare"] += game_gold_share
                    championList[player["championName"]]["lossGoldEfficiency"] += game_gold_efficiency

if position_match_count != 0:
    average_damage_share = average_damage_share / position_match_count
    average_gold_share = average_gold_share / position_match_count
    average_gold_efficiency = average_gold_efficiency / position_match_count

if win_number != 0:
    win_average_damage_share = win_average_damage_share / win_number
    win_average_gold_share = win_average_gold_share / win_number
    win_average_gold_efficiency = win_average_gold_efficiency / win_number

if lose_number != 0:
    lose_average_damage_share = lose_average_damage_share / lose_number
    lose_average_gold_share = lose_average_gold_share / lose_number
    lose_average_gold_efficiency = lose_average_gold_efficiency / lose_number

elements_to_print = [utils.format_to_print(
    {
        "Damage Share": average_damage_share,
        "Gold Share": average_gold_share,
        "Gold Efficiency": average_gold_efficiency,
        "winDamage Share": win_average_damage_share,
        "winGold Share": win_average_gold_share,
        "winGold Efficiency": win_average_gold_efficiency,
        "lossDamage Share": lose_average_damage_share,
        "lossGold Share": lose_average_gold_share,
        "lossGold Efficiency": lose_average_gold_efficiency,
        "wins": win_number,
        "losses": lose_number
    }, position_match_count, ingame_position
)]

for c in championList:
    champion = championList[c]
    champion["damageShare"] = champion["damageShare"] / champion["gameCount"]
    champion["goldShare"] = champion["goldShare"] / champion["gameCount"]
    champion["goldEfficiency"] = champion["goldEfficiency"] / champion["gameCount"]

    if champion["wins"] != 0:
        champion["winDamageShare"] = champion["winDamageShare"] / champion["wins"]
        champion["winGoldShare"] = champion["winGoldShare"] / champion["wins"]
        champion["winGoldEfficiency"] = champion["winGoldEfficiency"] / champion["wins"]

    if champion["losses"] != 0:
        champion["lossDamageShare"] = champion["lossDamageShare"] / champion["losses"]
        champion["lossGoldShare"] = champion["lossGoldShare"] / champion["losses"]
        champion["lossGoldEfficiency"] = champion["lossGoldEfficiency"] / champion["losses"]

    elements_to_print.append(utils.format_to_print(
        {
            "Damage Share": champion['damageShare'],
            "Gold Share": champion['goldShare'],
            "Gold Efficiency": champion['goldEfficiency'],
            "winDamage Share": champion['winDamageShare'],
            "winGold Share": champion['winGoldShare'],
            "winGold Efficiency": champion['winGoldEfficiency'],
            "lossDamage Share": champion['lossDamageShare'],
            "lossGold Share": champion['lossGoldShare'],
            "lossGold Efficiency": champion['lossGoldEfficiency'],
            "wins": champion['wins'],
            "losses": champion['losses']
        }, champion['gameCount'], champion['championName']
    ))

utils.print_result(elements_to_print)
