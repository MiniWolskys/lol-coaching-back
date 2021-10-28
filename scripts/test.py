import requests

from LoLCoaching.config import config

base_url_euw = "https://euw1.api.riotgames.com"
base_url_europe = "https://europe.api.riotgames.com"

game = "lol"
summoner_api = "summoner/v4/summoners"
match_api = "match/v5/matches"
by_name = "by-name"
by_puuid = "by-puuid"

# Put the username of the player you want to see the stats.
# ingame_position is TOP, JUNGLE, MIDDLE, BOTTOM or UTILITY
username = "medo38"
ingame_position = "MIDDLE"
api_key = config.get_api_key()

url = f"{base_url_euw}/{game}/{summoner_api}/{by_name}/{username}?api_key={api_key}"

resp = requests.get(url)
data = resp.json()

puuid = data["puuid"]

url = f"{base_url_europe}/{game}/{match_api}/{by_puuid}/{puuid}/ids?start=0&count=30&api_key={api_key}"

resp = requests.get(url)
match_list = resp.json()

valid_match_list = []
pstats = []  # Stats for players
tstats = []  # Stats for teams

for match in match_list:
    url = f"{base_url_europe}/{game}/{match_api}/{match}?api_key={api_key}"
    resp = requests.get(url)
    data_json = resp.json()
    if "info" not in data_json:
        continue
    data = data_json["info"]
    win = False
    if data["mapId"] == 11 and data["gameMode"] == "CLASSIC" and data["gameType"] == "MATCHED_GAME":
        i = 0
        for participant in data["participants"]:
            if participant["puuid"] == puuid:
                win = participant["win"]
        pstats.append(data["participants"])
        tstats.append(data["teams"])
        valid_match_list.append({"Id": match, "win": win})

p_stats = []

for match in pstats:
    team_won = 0
    team_1_damage = 0
    team_2_damage = 0
    team_1_gold = 0
    team_2_gold = 0
    for player in match:
        if player["teamId"] == 100:
            team_1_damage += player["totalDamageDealtToChampions"]
            team_1_gold += player["goldEarned"]
            if player["win"] is True:
                team_won = 1
            else:
                team_won = 2
        if player["teamId"] == 200:
            team_2_damage += player["totalDamageDealtToChampions"]
            team_2_gold += player["goldEarned"]
    for player in match:
        if player["teamId"] == 100:
            p_stats.append({"playerName": player["summonerName"], "champion": player["championName"], "win": player["win"], "damageShare": player["totalDamageDealtToChampions"] / team_1_damage * 100, "position": player["teamPosition"], "goldEfficiency": player["totalDamageDealtToChampions"] / player["goldEarned"] * 100, "goldShare": player["goldEarned"] / team_1_gold * 100})
        if player["teamId"] == 200:
            p_stats.append({"playerName": player["summonerName"], "champion": player["championName"], "win": player["win"], "damageShare": player["totalDamageDealtToChampions"] / team_2_damage * 100, "position": player["teamPosition"], "goldEfficiency": player["totalDamageDealtToChampions"] / player["goldEarned"] * 100, "goldShare": player["goldEarned"] / team_2_gold * 100})

average_damage_share = 0
average_gold_share = 0
average_gold_efficiency = 0
position_match_count = 0

win_number = 0
win_average_damage_share = 0
win_average_gold_share = 0
win_average_gold_efficiency = 0

lose_number = 0
lose_average_damage_share = 0
lose_average_gold_share = 0
lose_average_gold_efficiency = 0

championList = {}

for player in p_stats:
    if player["playerName"] == username and player["position"] == ingame_position:
        if player["champion"] in championList:
            championList[player["champion"]]["damageShare"] += player["damageShare"]
            championList[player["champion"]]["goldShare"] += player["goldShare"]
            championList[player["champion"]]["goldEfficiency"] += player["goldEfficiency"]
            if player["win"] is True:
                championList[player["champion"]]["winDamageShare"] += player["damageShare"]
                championList[player["champion"]]["winGoldShare"] += player["goldShare"]
                championList[player["champion"]]["winGoldEfficiency"] += player["goldEfficiency"]
                championList[player["champion"]]["wins"] += 1
            else:
                championList[player["champion"]]["lossDamageShare"] += player["damageShare"]
                championList[player["champion"]]["lossGoldShare"] += player["goldShare"]
                championList[player["champion"]]["lossGoldEfficiency"] += player["goldEfficiency"]
                championList[player["champion"]]["losses"] += 1
        else:
            championList[player["champion"]] = {}
            championList[player["champion"]]["championName"] = player["champion"]
            championList[player["champion"]]["damageShare"] = player["damageShare"]
            championList[player["champion"]]["goldShare"] = player["goldShare"]
            championList[player["champion"]]["goldEfficiency"] = player["goldEfficiency"]
            if player["win"] is True:
                championList[player["champion"]]["lossDamageShare"] = 0
                championList[player["champion"]]["lossGoldShare"] = 0
                championList[player["champion"]]["lossGoldEfficiency"] = 0
                championList[player["champion"]]["losses"] = 0
                championList[player["champion"]]["winDamageShare"] = player["damageShare"]
                championList[player["champion"]]["winGoldShare"] = player["goldShare"]
                championList[player["champion"]]["winGoldEfficiency"] = player["goldEfficiency"]
                championList[player["champion"]]["wins"] = 1
            else:
                championList[player["champion"]]["winDamageShare"] = 0
                championList[player["champion"]]["winGoldShare"] = 0
                championList[player["champion"]]["winGoldEfficiency"] = 0
                championList[player["champion"]]["wins"] = 0
                championList[player["champion"]]["lossDamageShare"] = player["damageShare"]
                championList[player["champion"]]["lossGoldShare"] = player["goldShare"]
                championList[player["champion"]]["lossGoldEfficiency"] = player["goldEfficiency"]
                championList[player["champion"]]["losses"] = 1
        if player["win"] is True:
            win_number += 1
            win_average_damage_share += player["damageShare"]
            win_average_gold_share += player["goldShare"]
            win_average_gold_efficiency += player["goldEfficiency"]
        else:
            lose_number += 1
            lose_average_damage_share += player["damageShare"]
            lose_average_gold_share += player["goldShare"]
            lose_average_gold_efficiency += player["goldEfficiency"]
        average_damage_share += player["damageShare"]
        average_gold_share += player["goldShare"]
        average_gold_efficiency += player["goldEfficiency"]
        position_match_count += 1

average_damage_share = average_damage_share / position_match_count if position_match_count != 0 else 0
average_gold_share = average_gold_share / position_match_count if position_match_count != 0 else 0
average_gold_efficiency = average_gold_efficiency / position_match_count if position_match_count != 0 else 0

win_average_damage_share = win_average_damage_share / win_number if win_number != 0 else 0
win_average_gold_share = win_average_gold_share / win_number if win_number != 0 else 0
win_average_gold_efficiency = win_average_gold_efficiency / win_number if win_number != 0 else 0

lose_average_damage_share = lose_average_damage_share / lose_number if lose_number != 0 else 0
lose_average_gold_share = lose_average_gold_share / lose_number if lose_number != 0 else 0
lose_average_gold_efficiency = lose_average_gold_efficiency / lose_number if lose_number != 0 else 0

print(f"On {position_match_count} games as {ingame_position}:")
print(f"\tDamage share : {average_damage_share:.2f}%")
print(f"\tGold share : {average_gold_share:.2f}%")
print(f"\tGold efficiency : {average_gold_efficiency:.2f}%")

print(f"On {win_number} wins :")
print(f"\tDamage share : {win_average_damage_share:.2f}%")
print(f"\tGold share : {win_average_gold_share:.2f}%")
print(f"\tGold efficiency : {win_average_gold_efficiency:.2f}%")

print(f"On {lose_number} losses :")
print(f"\tDamage share : {lose_average_damage_share:.2f}%")
print(f"\tGold share : {lose_average_gold_share:.2f}%")
print(f"\tGold efficiency : {lose_average_gold_efficiency:.2f}%")

for c in championList:
    champion = championList[c]
    champion["damageShare"] = champion["damageShare"] / (champion["wins"] + champion["losses"])
    champion["goldShare"] = champion["goldShare"] / (champion["wins"] + champion["losses"])
    champion["goldEfficiency"] = champion["goldEfficiency"] / (champion["wins"] + champion["losses"])

    champion["winDamageShare"] = champion["winDamageShare"] / champion["wins"] if champion["wins"] != 0 else 0
    champion["winGoldShare"] = champion["winGoldShare"] / champion["wins"] if champion["wins"] != 0 else 0
    champion["winGoldEfficiency"] = champion["winGoldEfficiency"] / champion["wins"] if champion["wins"] != 0 else 0

    champion["lossDamageShare"] = champion["lossDamageShare"] / champion["losses"] if champion["losses"] != 0 else 0
    champion["lossGoldShare"] = champion["lossGoldShare"] / champion["losses"] if champion["losses"] != 0 else 0
    champion["lossGoldEfficiency"] = champion["lossGoldEfficiency"] / champion["losses"] if champion["losses"] != 0 else 0

    print("----------------------------------------------")

    print(f"On {champion['wins'] + champion['losses']} as {champion['championName']}:")
    print(f"\tDamage share : {champion['damageShare']:.2f}%")
    print(f"\tGold share : {champion['goldShare']:.2f}%")
    print(f"\tGold efficiency : {champion['goldEfficiency']:.2f}%")

    print(f"On {champion['wins']:} wins :")
    print(f"\tDamage share : {champion['winDamageShare']:.2f}%")
    print(f"\tGold share : {champion['winGoldShare']:.2f}%")
    print(f"\tGold efficiency : {champion['winGoldEfficiency']:.2f}%")

    print(f"On {champion['losses']:} losses :")
    print(f"\tDamage share : {champion['lossDamageShare']:.2f}%")
    print(f"\tGold share : {champion['lossGoldShare']:.2f}%")
    print(f"\tGold efficiency : {champion['lossGoldEfficiency']:.2f}%")
