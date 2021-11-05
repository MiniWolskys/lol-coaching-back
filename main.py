import requests
import sys

from LoLCoaching.config import config

# RIOT API Related informations
BASE_URL_EUW = "https://euw1.api.riotgames.com"
BASE_URL_EUROPE = "https://europe.api.riotgames.com"
GAME = "lol"
SUMMONER_API = "summoner/v4/summoners"
MATCH_API = "match/v5/matches"
BY_NAME = "by-name"
BY_PUUID = "by-puuid"

# Getting RIOT API key defined in config.ini
api_key = config.get_api_key()


class Data:
    def __init__(self, teams_data, specific_data, data_at_x):
        self.teams_data_set = teams_data
        self.specific_data_set = specific_data
        self.data_at_x_set = data_at_x
        self.data = {}
        self.win_data = {}
        self.lose_data = {}
        for elem in teams_data:
            self.data[elem] = 0.0
            self.win_data[elem] = 0.0
            self.lose_data[elem] = 0.0
        for elem in specific_data:
            self.data[elem] = 0.0
            self.win_data[elem] = 0.0
            self.lose_data[elem] = 0.0
        for elem in data_at_x:
            self.data[elem] = 0.0
            self.win_data[elem] = 0.0
            self.lose_data[elem] = 0.0
        self.count = 0
        self.win_count = 0
        self.lose_count = 0

    def add_data(self, match):
        for elem in self.data:
            if elem in self.teams_data_set:
                self.data[elem] += match[elem]
            elif elem in self.specific_data_set:
                self.data[elem] += match[elem]
            elif elem in self.data_at_x_set:
                for key in match:
                    if "stat_at_" in key:
                        self.data[elem] += match[key][elem]
        self.count += 1
        if match["win"] is True:
            for elem in self.win_data:
                if elem in self.teams_data_set:
                    self.win_data[elem] += match[elem]
                elif elem in self.specific_data_set:
                    self.win_data[elem] += match[elem]
                elif elem in self.data_at_x_set:
                    for key in match:
                        if "stat_at_" in key:
                            self.win_data[elem] += match[key][elem]
            self.win_count += 1
        else:
            for elem in self.lose_data:
                if elem in self.teams_data_set:
                    self.lose_data[elem] += match[elem]
                elif elem in self.specific_data_set:
                    self.lose_data[elem] += match[elem]
                elif elem in self.data_at_x_set:
                    for key in match:
                        if "stat_at_" in key:
                            self.lose_data[elem] += match[key][elem]
            self.lose_count += 1

    def make_average(self):
        for elem in self.data:
            if self.count > 0:
                self.data[elem] = self.data[elem] / self.count
            if self.win_count > 0:
                self.win_data[elem] = self.win_data[elem] / self.win_count
            if self.lose_count > 0:
                self.lose_data[elem] = self.lose_data[elem] / self.lose_count

    def print(self):
        print(self.data, self.count)
        print(self.win_data, self.win_count)
        print(self.lose_data, self.lose_count)


def get_team_data_list():
    return {"damageShare": "totalDamageDealtToChampions", "goldShare": "goldEarned"}


def get_specific_data_list():
    return {"goldEfficiency": "goldEfficiency"}


def get_at_x_data_list():
    return {"totalGold": "totalGold", "deaths": "deaths", "k+a": "k+a"}


def check_position(position: str) -> bool:
    if position in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]:
        return True
    return False


def calculate_gold_efficiency(goldEarned: int, damageDealt: int) -> float:
    player_efficiency = damageDealt / goldEarned * 100
    return player_efficiency


def get_player_puuid(username: str) -> str:
    url = f"{BASE_URL_EUW}/{GAME}/{SUMMONER_API}/{BY_NAME}/{username}?api_key={api_key}"
    resp = requests.get(url)
    data = resp.json()
    if "puuid" not in data:
        raise Exception(f"No user found for username {username}, check API KEY is still valid and user is correct.")
    puuid = data["puuid"]
    return puuid


def get_player_last_games(puuid: str, count: int) -> list:
    url = f"{BASE_URL_EUROPE}/{GAME}/{MATCH_API}/{BY_PUUID}/{puuid}/ids?start=0&count={count}&api_key={api_key}"
    resp = requests.get(url)
    match_list = resp.json()
    return match_list


def check_player_position(match_stat: dict, name=None, puuid=None, position=None) -> bool:
    if (name is None and puuid is None) or position is None:
        if name is None and puuid is None:
            raise Exception("At least name or puuid need to be specified to check_player_position function.")
        else:
            raise Exception("A position need to be specified for check_player_position function.")
    for participant in match_stat["participants"]:
        if (participant["summonerName"] == name or participant["puuid"] == puuid)\
                and participant["teamPosition"] == position:
            return True
    return False


def is_match_valid(match_stat: dict) -> bool:
    if match_stat["mapId"] == 11 and match_stat["gameMode"] == "CLASSIC" and match_stat["gameType"] == "MATCHED_GAME"\
            and match_stat["gameDuration"] > 901:
        return True
    return False


def get_match_stats(match_id: str) -> dict:
    url = f"{BASE_URL_EUROPE}/{GAME}/{MATCH_API}/{match_id}?api_key={api_key}"
    resp = requests.get(url)
    data_json = resp.json()
    if "info" not in data_json:
        raise Exception(f"No information retrieved for match {match_id}")
    data = data_json["info"]
    return data


def get_extra_data_at_minute(data: dict, minute: int) -> dict:
    target_frame = 0
    for frame in data["frames"]:
        if 60000 * minute < frame["timestamp"]:
            target_frame = frame
            for participantNumber in frame["participantFrames"]:
                participant = frame["participantFrames"][participantNumber]
                participant["k+a"] = 0
                participant["deaths"] = 0
            break
    for frame in data["frames"]:
        if frame["timestamp"] < 60000 * (minute + 1):
            events = frame["events"]
            for event in events:
                if event["type"] == "CHAMPION_KILL":
                    if event["killerId"] != 0:
                        target_frame["participantFrames"][str(event["killerId"])]["k+a"] += 1
                        target_frame["participantFrames"][str(event["victimId"])]["deaths"] += 1
    return data


def get_stats_at_minute(match_id: str, minute: int) -> dict:
    url = f"{BASE_URL_EUROPE}/{GAME}/{MATCH_API}/{match_id}/timeline?api_key={api_key}"
    resp = requests.get(url)
    data_json = resp.json()
    if "info" not in data_json:
        raise Exception(f"No information retrieved for match {match_id}")
    data = data_json["info"]
    data = get_extra_data_at_minute(data, minute)
    for frame in data["frames"]:
        if 60000 * (minute + 1) > frame["timestamp"] > 60000 * minute:
            return {"timestamp": frame["timestamp"], "data": frame["participantFrames"]}
    return {}


def aggregate_data(match_data: dict, minutes_data=None, team_data=None) -> dict:
    if minutes_data is not None:
        for minute in minutes_data:
            timestamp = minute["timestamp"]
            minute_data = minute["data"]
            for player in match_data["participants"]:
                player[f"stat_at_{timestamp}"] = minute_data[str(player["participantId"])]
    if team_data is not None:
        for team in match_data["teams"]:
            if team["teamId"] == 100:
                team.update(team_data["100"])
            if team["teamId"] == 200:
                team.update(team_data["200"])
    return match_data


def create_team_stats(match_data: dict, data_list: dict) -> dict:
    team_data = {"100": {}, "200": {}}
    for elem in data_list:
        team_data["100"][data_list[elem]] = 0
        team_data["200"][data_list[elem]] = 0
    for player in match_data["participants"]:
        for elem in data_list:
            team_data[str(player["teamId"])][data_list[elem]] += player[data_list[elem]]
    return team_data


def get_player_data(match_data: dict, username: str, share_team_stat=None) -> dict:
    for player in match_data["participants"]:
        if player["summonerName"] == username:
            if share_team_stat is not None:
                for elem in share_team_stat:
                    player[elem] = player[share_team_stat[elem]] /\
                                   match_data["teams"][int(player["teamId"]/100-1)][share_team_stat[elem]] * 100
            player["goldEfficiency"] = calculate_gold_efficiency(player["goldEarned"],
                                                                 player["totalDamageDealtToChampions"])
            player["k+a"] = player["kills"] + player["assists"]
            return player
    return {}


def get_set_data(match_list, username, position):
    team_data_list = get_team_data_list()
    player_stats = []
    for match in match_list:
        data = get_match_stats(match)
        if is_match_valid(data) is True and check_player_position(data, name=username, position=position) is True:
            data_at_15 = get_stats_at_minute(match, 15)
            team_data = create_team_stats(data, team_data_list)
            match_data = aggregate_data(data, minutes_data=[data_at_15], team_data=team_data)
            player_stats.append(get_player_data(match_data, username, team_data_list))
    return player_stats


def get_match_list(username: str, count: int) -> list:
    puuid = get_player_puuid(username)
    match_list = get_player_last_games(puuid, count)
    return match_list


def get_champion_list(player_stats: list) -> list:
    champion_list = []
    for game in player_stats:
        if game["championName"] not in champion_list:
            champion_list.append(game["championName"])
    return champion_list


def main():
    if len(sys.argv) < 3:
        return 0
    username = sys.argv[1]
    position = sys.argv[2]
    match_list = get_match_list(username, 40)
    player_stats = get_set_data(match_list, username, position)
    champion_list = get_champion_list(player_stats)
    specific_data = get_specific_data_list()
    team_data = get_team_data_list()
    at_x_data = get_at_x_data_list()
    average_data = Data(team_data, specific_data, at_x_data)
    champion_data = {}
    for champion in champion_list:
        champion_data[champion] = Data(team_data, specific_data, at_x_data)
    for game in player_stats:
        average_data.add_data(game)
        for champion in champion_list:
            if game["championName"] == champion:
                champion_data[champion].add_data(game)
    average_data.make_average()
    average_data.print()
    for champion in champion_list:
        champion_data[champion].make_average()
        print(champion, ":")
        champion_data[champion].print()


main()





























# ### SETUP PHASE ###
#
# # Put the username of the player you want to see the stats.
# # ingame_position is TOP, JUNGLE, MIDDLE, BOTTOM or UTILITY
# username = "MiniWolskys"
# ingame_position = "MIDDLE"
#
# # Stats to retrieve
# stats_to_retrieve_share = {
#     "damageShare": "totalDamageDealtToChampions",
#     "goldShare": "goldEarned",
# }
#
# stats_to_retrieve_team = {
#     "heraldKilled": "riftHerald",
#     "baronKilled": "baron"
# }
#
# stats_to_retrieve = {
#     "visionScore": "visionScore",
#     "controlScore": "timeCCingOthers"
# }
#
# # Total stats
# position_match_count = 0
# average_stats = {}
# for elem in stats_to_retrieve_share:
#     average_stats[elem] = 0
# for elem in stats_to_retrieve_team:
#     average_stats[elem] = 0
# for elem in stats_to_retrieve:
#     average_stats[elem] = 0
# average_gold_efficiency = 0
#
# # Stats in wins
# win_number = 0
# win_stats = {}
# for elem in stats_to_retrieve_share:
#     win_stats[elem] = 0
# for elem in stats_to_retrieve_team:
#     win_stats[elem] = 0
# for elem in stats_to_retrieve:
#     win_stats[elem] = 0
# win_average_gold_efficiency = 0
#
# # Stats in losses
# lose_number = 0
# loss_stats = {}
# for elem in stats_to_retrieve_share:
#     loss_stats[elem] = 0
# for elem in stats_to_retrieve_team:
#     loss_stats[elem] = 0
# for elem in stats_to_retrieve:
#     loss_stats[elem] = 0
# lose_average_gold_efficiency = 0
#
# # championList is a dictionary of all champions played at given position with detailed stats for the champion.
# championList = {}
#
# # Getting all stats for match
# # match_id: {"final_stats": end_game_stats, "15_stats": stats_at_15}
# match_stats = {}
#
# ### GAME STATS ###


        # team_1_stats = {}
        # team_2_stats = {}
        # for elem in stats_to_retrieve_share:
        #     team_1_stats[elem] = 0
        #     team_2_stats[elem] = 0
        # team_1_gold = 0
        # team_2_gold = 0
        #
        # # Calculating total damage and gold of the team
        # for player in data["participants"]:
        #     if player["teamId"] == 100:
        #         for elem in stats_to_retrieve_share:
        #             team_1_stats[elem] += player[stats_to_retrieve_share[elem]]
        #     if player["teamId"] == 200:
        #         for elem in stats_to_retrieve_share:
        #             team_2_stats[elem] += player[stats_to_retrieve_share[elem]]
        #
        # # Getting player specific information
        # for player in data["participants"]:
        #     if player["summonerName"] == username and player["teamPosition"] == ingame_position:
        #         # Save that specific match so we can get the timeline details about it.
        #         valid_match_list[match] = {"lookAt": player["participantId"]}
        #         valid_match_list[match]["player"] = []
        #         for tmp_player in data["participants"]:
        #             valid_match_list[match]["player"].append({"participantId": tmp_player["participantId"],
        #                                                  "position": tmp_player["teamPosition"]})
        #
        #         # If champion is not in championList, we set all values to get the list ready.
        #         if player["championName"] not in championList:
        #             championList[player["championName"]] = {}
        #             championList[player["championName"]]["championName"] = player["championName"]
        #             championList[player["championName"]]["gameCount"] = 0
        #             championList[player["championName"]]["wins"] = 0
        #             championList[player["championName"]]["losses"] = 0
        #             for elem in stats_to_retrieve_share:
        #                 championList[player["championName"]][elem] = 0
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
        #             for elem in stats_to_retrieve:
        #                 championList[player["championName"]][elem] = 0
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
        #             for elem in stats_to_retrieve_team:
        #                 championList[player["championName"]][elem] = 0
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] = 0
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] = 0
        #             championList[player["championName"]]["goldEfficiency"] = 0
        #             championList[player["championName"]]["winGoldEfficiency"] = 0
        #             championList[player["championName"]]["lossGoldEfficiency"] = 0
        #
        #         # Calculate share of gold, damage, and gold efficiency.
        #         game_stats = {}
        #         for elem in stats_to_retrieve:
        #             game_stats[elem] = player[stats_to_retrieve[elem]]
        #         for elem in stats_to_retrieve_team:
        #             game_stats[elem] = data["teams"][int(player["teamId"]/100-1)]["objectives"][stats_to_retrieve_team[elem]]["kills"]
        #         game_gold_efficiency = player["totalDamageDealtToChampions"] / player["goldEarned"] * 100
        #         if player["teamId"] == 100:
        #             for elem in stats_to_retrieve_share:
        #                 game_stats[elem] = player[stats_to_retrieve_share[elem]] / team_1_stats[elem] * 100
        #         if player["teamId"] == 200:
        #             for elem in stats_to_retrieve_share:
        #                 game_stats[elem] = player[stats_to_retrieve_share[elem]] / team_2_stats[elem] * 100
        #
        #         # Add overall stats
        #         for elem in stats_to_retrieve_share:
        #             average_stats[elem] += game_stats[elem]
        #         for elem in stats_to_retrieve:
        #             average_stats[elem] += game_stats[elem]
        #         for elem in stats_to_retrieve_team:
        #             average_stats[elem] += game_stats[elem]
        #
        #         average_gold_efficiency += game_gold_efficiency
        #         position_match_count += 1
        #         if player["win"] is True:
        #             for elem in stats_to_retrieve_share:
        #                 win_stats[elem] += game_stats[elem]
        #             for elem in stats_to_retrieve:
        #                 win_stats[elem] += game_stats[elem]
        #             for elem in stats_to_retrieve_team:
        #                 win_stats[elem] += game_stats[elem]
        #             win_average_gold_efficiency += game_gold_efficiency
        #             win_number += 1
        #         else:
        #             for elem in stats_to_retrieve_share:
        #                 loss_stats[elem] += game_stats[elem]
        #             for elem in stats_to_retrieve:
        #                 loss_stats[elem] += game_stats[elem]
        #             for elem in stats_to_retrieve_team:
        #                 loss_stats[elem] += game_stats[elem]
        #             lose_average_gold_efficiency += game_gold_efficiency
        #             lose_number += 1
        #
        #         # Add champion specific stats
        #         championList[player["championName"]]["gameCount"] += 1
        #         for elem in stats_to_retrieve_share:
        #             championList[player["championName"]][elem] += game_stats[elem]
        #         for elem in stats_to_retrieve:
        #             championList[player["championName"]][elem] += game_stats[elem]
        #         for elem in stats_to_retrieve_team:
        #             championList[player["championName"]][elem] += game_stats[elem]
        #         championList[player["championName"]]["goldEfficiency"] += game_gold_efficiency
        #         if player["win"] is True:
        #             championList[player["championName"]]["wins"] += 1
        #             for elem in stats_to_retrieve_share:
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             for elem in stats_to_retrieve:
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             for elem in stats_to_retrieve_team:
        #                 championList[player["championName"]][f"win{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             championList[player["championName"]]["winGoldEfficiency"] += game_gold_efficiency
        #         else:
        #             championList[player["championName"]]["losses"] += 1
        #             for elem in stats_to_retrieve_share:
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             for elem in stats_to_retrieve:
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             for elem in stats_to_retrieve_team:
        #                 championList[player["championName"]][f"loss{elem[0].upper()}{elem[1:]}"] += game_stats[elem]
        #             championList[player["championName"]]["lossGoldEfficiency"] += game_gold_efficiency

### TIMELINE STATS ###

# for match in valid_match_list:
#     url = f"{base_url_europe}/{game}/{match_api}/{match}/timeline?api_key={api_key}"
#     resp = requests.get(url)
#     data_json = resp.json()
#     if "info" not in data_json:
#         continue
#     data = data_json["info"]
#     for frame in data["frames"]:
#         if 60000 * 16 > frame["timestamp"] > 60000 * 15:
#
#
# # TODO :
# # REWORK :
# # Get all data for each game where player is a desired position, then analyse it after.
#
#
# ### CALCULATING STATS AVERAGE ###
#
# # Calculating average of stats
# if position_match_count != 0:
#     for elem in stats_to_retrieve_share:
#         average_stats[elem] = average_stats[elem] / position_match_count
#     for elem in stats_to_retrieve:
#         average_stats[elem] = average_stats[elem] / position_match_count
#     for elem in stats_to_retrieve_team:
#         average_stats[elem] = average_stats[elem] / position_match_count
#     average_gold_efficiency = average_gold_efficiency / position_match_count
#
# if win_number != 0:
#     for elem in stats_to_retrieve_share:
#         win_stats[elem] = win_stats[elem] / win_number
#     for elem in stats_to_retrieve:
#         win_stats[elem] = win_stats[elem] / win_number
#     for elem in stats_to_retrieve_team:
#         win_stats[elem] = win_stats[elem] / win_number
#     win_average_gold_efficiency = win_average_gold_efficiency / win_number
#
# if lose_number != 0:
#     for elem in stats_to_retrieve_share:
#         loss_stats[elem] = loss_stats[elem] / lose_number
#     for elem in stats_to_retrieve:
#         loss_stats[elem] = loss_stats[elem] / lose_number
#     for elem in stats_to_retrieve_team:
#         loss_stats[elem] = loss_stats[elem] / lose_number
#     lose_average_gold_efficiency = lose_average_gold_efficiency / lose_number
#
# # Creating array to pass to format_to_print function
# array = {}
# for elem in stats_to_retrieve_share:
#     printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#     array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
#     array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
#     array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
# for elem in stats_to_retrieve:
#     printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#     array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
#     array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
#     array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
# for elem in stats_to_retrieve_team:
#     printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#     array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = average_stats[elem]
#     array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = win_stats[elem]
#     array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] = loss_stats[elem]
# array["Gold Efficiency"] = average_gold_efficiency
# array["winGold Efficiency"] = win_average_gold_efficiency
# array["lossGold Efficiency"] = lose_average_gold_efficiency
# array["wins"] = win_number
# array["losses"] = lose_number
#
# # Getting general stats ready to print
# elements_to_print = [utils.format_to_print(array, position_match_count, ingame_position)]
#
# for c in championList:
#     champion = championList[c]
#     for elem in stats_to_retrieve_share:
#         champion[elem] = champion[elem] / champion["gameCount"]
#     for elem in stats_to_retrieve:
#         champion[elem] = champion[elem] / champion["gameCount"]
#     for elem in stats_to_retrieve_team:
#         champion[elem] = champion[elem] / champion["gameCount"]
#     champion["goldEfficiency"] = champion["goldEfficiency"] / champion["gameCount"]
#
#     if champion["wins"] != 0:
#         for elem in stats_to_retrieve_share:
#             champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["wins"]
#         for elem in stats_to_retrieve:
#             champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["wins"]
#         for elem in stats_to_retrieve_team:
#             champion[f"win{elem[0].upper()}{elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["wins"]
#         champion["winGoldEfficiency"] = champion["winGoldEfficiency"] / champion["wins"]
#
#     if champion["losses"] != 0:
#         for elem in stats_to_retrieve_share:
#             champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["losses"]
#         for elem in stats_to_retrieve:
#             champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["losses"]
#         for elem in stats_to_retrieve_team:
#             champion[f"loss{elem[0].upper()}{elem[1:]}"] = champion[f"loss{elem[0].upper()}{elem[1:]}"]\
#                                                           / champion["losses"]
#         champion["lossGoldEfficiency"] = champion["lossGoldEfficiency"] / champion["losses"]
#
#     champion_array = {}
#     for elem in stats_to_retrieve_share:
#         printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#         champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
#         champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
#         champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
#             champion[f"loss{elem[0].upper()}{elem[1:]}"]
#     for elem in stats_to_retrieve:
#         printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#         champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
#         champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
#         champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
#             champion[f"loss{elem[0].upper()}{elem[1:]}"]
#     for elem in stats_to_retrieve_team:
#         printed_elem = " ".join([s for s in re.split("([A-Z][^A-Z]*)", elem) if s])
#         champion_array[f"{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[elem]
#         champion_array[f"win{printed_elem[0].upper()}{printed_elem[1:]}"] = champion[f"win{elem[0].upper()}{elem[1:]}"]
#         champion_array[f"loss{printed_elem[0].upper()}{printed_elem[1:]}"] =\
#             champion[f"loss{elem[0].upper()}{elem[1:]}"]
#     champion_array["Gold Efficiency"] = champion["goldEfficiency"]
#     champion_array["winGold Efficiency"] = champion["winGoldEfficiency"]
#     champion_array["lossGold Efficiency"] = champion["lossGoldEfficiency"]
#     champion_array["wins"] = champion["wins"]
#     champion_array["losses"] = champion["losses"]
#
#     elements_to_print.append(utils.format_to_print(champion_array, champion['gameCount'], champion['championName']))
#
# ### PRINTING STATS ###
#
# # utils.print_result(elements_to_print)