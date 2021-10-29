import requests
import re

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
username = "Ilowa"
ingame_position = "BOTTOM"

# Stats to retrieve
stats_to_retrieve_share = {
    "damageShare": "totalDamageDealtToChampions",
    "goldShare": "goldEarned",
}

stats_to_retrieve_team = {
    "heraldKilled": "riftHerald",
    "baronKilled": "baron"
}

stats_to_retrieve = {
    "visionScore": "visionScore"
}

# Getting RIOT API key defined in config.ini
api_key = config.get_api_key()

# Getting player puuid to retrieve games.
url = f"{base_url_euw}/{game}/{summoner_api}/{by_name}/{username}?api_key={api_key}"
resp = requests.get(url)
data = resp.json()
puuid = data["puuid"]

# Getting last 30 games played by player.
url = f"{base_url_europe}/{game}/{match_api}/{by_puuid}/{puuid}/ids?start=0&count=30&api_key={api_key}"
resp = requests.get(url)
match_list = resp.json()

# Total stats
position_match_count = 0
average_stats = {}
for elem in stats_to_retrieve_share:
    average_stats[elem] = 0
for elem in stats_to_retrieve_team:
    average_stats[elem] = 0
for elem in stats_to_retrieve:
    average_stats[elem] = 0
average_gold_efficiency = 0

# Stats in wins
win_number = 0
win_stats = {}
for elem in stats_to_retrieve_share:
    win_stats[elem] = 0
for elem in stats_to_retrieve_team:
    win_stats[elem] = 0
for elem in stats_to_retrieve:
    win_stats[elem] = 0
win_average_gold_efficiency = 0

# Stats in losses
lose_number = 0
loss_stats = {}
for elem in stats_to_retrieve_share:
    loss_stats[elem] = 0
for elem in stats_to_retrieve_team:
    loss_stats[elem] = 0
for elem in stats_to_retrieve:
    loss_stats[elem] = 0
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
        team_1_stats = {}
        team_2_stats = {}
        for elem in stats_to_retrieve_share:
            team_1_stats[elem] = 0
            team_2_stats[elem] = 0
        team_1_gold = 0
        team_2_gold = 0

        # Calculating total damage and gold of the team
        for player in data["participants"]:
            if player["teamId"] == 100:
                for elem in stats_to_retrieve_share:
                    team_1_stats[elem] += player[stats_to_retrieve_share[elem]]
            if player["teamId"] == 200:
                for elem in stats_to_retrieve_share:
                    team_2_stats[elem] += player[stats_to_retrieve_share[elem]]

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
                    for elem in stats_to_retrieve_share:
                        championList[player["championName"]][elem] = 0
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
                    for elem in stats_to_retrieve:
                        championList[player["championName"]][elem] = 0
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
                    for elem in stats_to_retrieve_team:
                        championList[player["championName"]][elem] = 0
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
                    championList[player["championName"]]["goldEfficiency"] = 0
                    championList[player["championName"]]["winGoldEfficiency"] = 0
                    championList[player["championName"]]["lossGoldEfficiency"] = 0

                # Calculate share of gold, damage, and gold efficiency.
                game_stats = {}
                for elem in stats_to_retrieve:
                    game_stats[elem] = player[stats_to_retrieve[elem]]
                for elem in stats_to_retrieve_team:
                    game_stats[elem] = data["teams"][int(player["teamId"]/100-1)]["objectives"][stats_to_retrieve_team[elem]]["kills"]
                game_gold_efficiency = player["totalDamageDealtToChampions"] / player["goldEarned"] * 100
                if player["teamId"] == 100:
                    for elem in stats_to_retrieve_share:
                        game_stats[elem] = player[stats_to_retrieve_share[elem]] / team_1_stats[elem] * 100
                if player["teamId"] == 200:
                    for elem in stats_to_retrieve_share:
                        game_stats[elem] = player[stats_to_retrieve_share[elem]] / team_2_stats[elem] * 100

                # Add overall stats
                for elem in stats_to_retrieve_share:
                    average_stats[elem] += game_stats[elem]
                for elem in stats_to_retrieve:
                    average_stats[elem] += game_stats[elem]
                for elem in stats_to_retrieve_team:
                    average_stats[elem] += game_stats[elem]

                average_gold_efficiency += game_gold_efficiency
                position_match_count += 1
                if player["win"] is True:
                    for elem in stats_to_retrieve_share:
                        win_stats[elem] += game_stats[elem]
                    for elem in stats_to_retrieve:
                        win_stats[elem] += game_stats[elem]
                    for elem in stats_to_retrieve_team:
                        win_stats[elem] += game_stats[elem]
                    win_average_gold_efficiency += game_gold_efficiency
                    win_number += 1
                else:
                    for elem in stats_to_retrieve_share:
                        loss_stats[elem] += game_stats[elem]
                    for elem in stats_to_retrieve:
                        loss_stats[elem] += game_stats[elem]
                    for elem in stats_to_retrieve_team:
                        loss_stats[elem] += game_stats[elem]
                    lose_average_gold_efficiency += game_gold_efficiency
                    lose_number += 1

                # Add champion specific stats
                championList[player["championName"]]["gameCount"] += 1
                for elem in stats_to_retrieve_share:
                    championList[player["championName"]][elem] += game_stats[elem]
                for elem in stats_to_retrieve:
                    championList[player["championName"]][elem] += game_stats[elem]
                for elem in stats_to_retrieve_team:
                    championList[player["championName"]][elem] += game_stats[elem]
                championList[player["championName"]]["goldEfficiency"] += game_gold_efficiency
                if player["win"] is True:
                    championList[player["championName"]]["wins"] += 1
                    for elem in stats_to_retrieve_share:
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    for elem in stats_to_retrieve:
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    for elem in stats_to_retrieve_team:
                        championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    championList[player["championName"]]["winGoldEfficiency"] += game_gold_efficiency
                else:
                    championList[player["championName"]]["losses"] += 1
                    for elem in stats_to_retrieve_share:
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    for elem in stats_to_retrieve:
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    for elem in stats_to_retrieve_team:
                        championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
                    championList[player["championName"]]["lossGoldEfficiency"] += game_gold_efficiency

# Calculating average of stats
if position_match_count != 0:
    for elem in stats_to_retrieve_share:
        average_stats[elem] = average_stats[elem] / position_match_count
    for elem in stats_to_retrieve:
        average_stats[elem] = average_stats[elem] / position_match_count
    for elem in stats_to_retrieve_team:
        average_stats[elem] = average_stats[elem] / position_match_count
    average_gold_efficiency = average_gold_efficiency / position_match_count

if win_number != 0:
    for elem in stats_to_retrieve_share:
        win_stats[elem] = win_stats[elem] / win_number
    for elem in stats_to_retrieve:
        win_stats[elem] = win_stats[elem] / win_number
    for elem in stats_to_retrieve_team:
        win_stats[elem] = win_stats[elem] / win_number
    win_average_gold_efficiency = win_average_gold_efficiency / win_number

if lose_number != 0:
    for elem in stats_to_retrieve_share:
        loss_stats[elem] = loss_stats[elem] / lose_number
    for elem in stats_to_retrieve:
        loss_stats[elem] = loss_stats[elem] / lose_number
    for elem in stats_to_retrieve_team:
        loss_stats[elem] = loss_stats[elem] / lose_number
    lose_average_gold_efficiency = lose_average_gold_efficiency / lose_number

# Creating array to pass to format_to_print function
array = {}
for elem in stats_to_retrieve_share:
    printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
    array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
    array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
    array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
for elem in stats_to_retrieve:
    printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
    array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
    array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
    array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
for elem in stats_to_retrieve_team:
    printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
    array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
    array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
    array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
array["Gold Efficiency"] = average_gold_efficiency
array["winGold Efficiency"] = win_average_gold_efficiency
array["lossGold Efficiency"] = lose_average_gold_efficiency
array["wins"] = win_number
array["losses"] = lose_number

# Getting general stats ready to print
elements_to_print = [utils.format_to_print(array, position_match_count, ingame_position)]

for c in championList:
    champion = championList[c]
    for elem in stats_to_retrieve_share:
        champion[elem] = champion[elem] / champion["gameCount"]
    for elem in stats_to_retrieve:
        champion[elem] = champion[elem] / champion["gameCount"]
    for elem in stats_to_retrieve_team:
        champion[elem] = champion[elem] / champion["gameCount"]
    champion["goldEfficiency"] = champion["goldEfficiency"] / champion["gameCount"]

    if champion["wins"] != 0:
        for elem in stats_to_retrieve_share:
            champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["wins"]
        for elem in stats_to_retrieve:
            champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["wins"]
        for elem in stats_to_retrieve_team:
            champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["wins"]
        champion["winGoldEfficiency"] = champion["winGoldEfficiency"] / champion["wins"]

    if champion["losses"] != 0:
        for elem in stats_to_retrieve_share:
            champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["losses"]
        for elem in stats_to_retrieve:
            champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["losses"]
        for elem in stats_to_retrieve_team:
            champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
                                                          / champion["losses"]
        champion["lossGoldEfficiency"] = champion["lossGoldEfficiency"] / champion["losses"]

    champion_array = {}
    for elem in stats_to_retrieve_share:
        printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
        champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
        champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
        champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
            champion[f"loss{elem[0].upper()}{elem[1:]}"]
    for elem in stats_to_retrieve:
        printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
        champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
        champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
        champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
            champion[f"loss{elem[0].upper()}{elem[1:]}"]
    for elem in stats_to_retrieve_team:
        printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
        champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
        champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
        champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
            champion[f"loss{elem[0].upper()}{elem[1:]}"]
    champion_array["Gold Efficiency"] = champion["goldEfficiency"]
    champion_array["winGold Efficiency"] = champion["winGoldEfficiency"]
    champion_array["lossGold Efficiency"] = champion["lossGoldEfficiency"]
    champion_array["wins"] = champion["wins"]
    champion_array["losses"] = champion["losses"]

    elements_to_print.append(utils.format_to_print(champion_array, champion['gameCount'], champion['championName']))

utils.print_result(elements_to_print)
