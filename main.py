import requests
import csv
import time


from configuration.config import Config

class InputPlayer:
    def __init__(self, username, position, gameCount, region):
        self.username = username
        self.position = position
        self.gameCount = gameCount
        self.region = region
        self.puuid = None

    def setPuuid(self, puuid):
        self.puuid = puuid

    def getUsername(self):
        return self.username

    def getPuuid(self):
        return self.puuid

    def getPosition(self):
        return self.position

    def getRegion(self):
        return self.region

    def getGameCount(self):
        return self.gameCount


class Player:
    def __init__(self, username: str, team_data: dict, specific_data: dict, at_x_data: dict, champion_list: list) -> None:
        self.username = username
        self.all_data = Data(team_data, specific_data, at_x_data)
        self.champion_data = {}
        self.champion_list = champion_list

        for champion in champion_list:
            self.champion_data[champion] = Data(team_data, specific_data, at_x_data)

    def process_data(self, all_games):
        self.add_all_games_data(all_games)
        self.make_average()

    def make_average(self):
        self.all_data.make_average()
        for champion in self.champion_list:
            self.champion_data[champion].make_average()

    def add_all_games_data(self, all_games):
        for game in all_games:
            self.all_data.add_data(game)
            for champion in self.champion_list:
                if game["championName"] == champion:
                    self.champion_data[champion].add_data(game)

    def print_data(self):
        print(self.username, ":")
        self.all_data.print()
        for champion in self.champion_list:
            print(champion, ":")
            self.champion_data[champion].print()
        print("")

    def organize(self):
        res = [[self.username, self.all_data.count], ["wins", self.all_data.win_count], ["losses", self.all_data.lose_count]]
        for data in self.all_data.data:
            res[0].append(self.all_data.data[data])
            res[1].append(self.all_data.win_data[data])
            res[2].append(self.all_data.lose_data[data])
        for champion in self.champion_list:
            tmp_res = [champion, self.champion_data[champion].count]
            win_tmp_res = ["wins", self.champion_data[champion].win_count]
            lose_tmp_res = ["losses", self.champion_data[champion].lose_count]
            for data in self.champion_data[champion].data:
                tmp_res.append(self.champion_data[champion].data[data])
                win_tmp_res.append(self.champion_data[champion].win_data[data])
                lose_tmp_res.append(self.champion_data[champion].lose_data[data])
            res.append(tmp_res)
            res.append(win_tmp_res)
            res.append(lose_tmp_res)
        return res


class Data:
    def __init__(self, teams_data: dict, specific_data: dict, data_at_x: dict) -> None:
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

    def add_data(self, match: dict) -> None:
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

    def make_average(self) -> None:
        for elem in self.data:
            if self.count > 0:
                self.data[elem] = self.data[elem] / self.count
            if self.win_count > 0:
                self.win_data[elem] = self.win_data[elem] / self.win_count
            if self.lose_count > 0:
                self.lose_data[elem] = self.lose_data[elem] / self.lose_count

    def print(self) -> None:
        data_dict = get_data_dict()
        print(f"On {self.count} games:")
        for elem in self.data:
            print(f"\t{data_dict[elem]}: {self.data[elem]}")
        print(f"On {self.win_count} won games:")
        for elem in self.win_data:
            print(f"\t{data_dict[elem]}: {self.win_data[elem]}")
        print(f"On {self.lose_count} lost games:")
        for elem in self.lose_data:
            print(f"\t{data_dict[elem]}: {self.lose_data[elem]}")


class APIRequest:
    def __init__(self) -> None:
        self.api_request_count = 0

    def make_request(self, url: str) -> requests.Response:
        if self.api_request_count >= 100:
            time.sleep(120)
            self.api_request_count = 0
        self.api_request_count += 1
        req = requests.get(url)
        return req


def get_data_dict():
    return {
        "damageShare": "% of total team damage",
        "goldShare": "% of total team gold",
        "goldEfficiency": "% of damage dealt for each gold",
        "csmin": "cs / minute",
        "visionMinute": "vision / minute",
        "damageMinute": "damage / minute",
        "totalGold": "gold at 15",
        "deaths": "deaths at 15",
        "k+a": "kills plus assists at 15",
        "machin": "total number of jungle monster killed"
    }


def get_team_data_list():
    return {"damageShare": "totalDamageDealtToChampions", "goldShare": "goldEarned"}


def get_specific_data_list():
    return {
        "goldEfficiency": "goldEfficiency",
        "csmin": "csmin",
        "visionMinute": "visionMinute",
        "damageMinute": "damageMinute"
    }


def get_at_x_data_list():
    return {"totalGold": "totalGold", "deaths": "deaths", "k+a": "k+a"}


def check_position(position: str) -> bool:
    if position in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]:
        return True
    return False


def calculate_gold_efficiency(gold_earned: int, damage_dealt: int) -> float:
    player_efficiency = damage_dealt / gold_earned * 100
    return player_efficiency


def get_player_puuid(player: InputPlayer) -> str:
    url = f'{config.get(player.getRegion(), "BASE_URL_PLATFORM")}{config.get("SUMMONER", "BY_NAME")}{player.getUsername()}?api_key={api_key}'
    resp = api_request.make_request(url)
    data = resp.json()
    if "puuid" not in data:
        raise Exception(f"No user found for username {player.getUsername()}, check API KEY is still valid and user is correct.")
    puuid = data["puuid"]
    return puuid


def get_player_last_games(player: InputPlayer) -> list:
    url = f'{config.get(player.getRegion(), "BASE_URL_REGION")}{config.get("MATCH", "BY_PUUID")}{player.getPuuid()}/ids?start=0&count={player.getGameCount()}&api_key={api_key}'
    resp = api_request.make_request(url)
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


def get_game_duration(time_t: int) -> int:
    if time_t < 15000:
        return time_t
    return int(time_t / 1000)


def is_match_valid(match_stat: dict) -> bool:
    if match_stat["mapId"] == 11 and match_stat["gameMode"] == "CLASSIC" and match_stat["gameType"] == "MATCHED_GAME"\
            and get_game_duration(match_stat["gameDuration"]) > 900:
        return True
    return False


def get_match_stats(match_id: str, region: str) -> dict:
    url = f'{config.get(region, "BASE_URL_REGION")}{config.get("MATCH", "BY_MATCH_ID")}{match_id}?api_key={api_key}'
    resp = api_request.make_request(url)
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


def get_stats_at_minute(match_id: str, minute: int, region: str) -> dict:
    url = f'{config.get(region, "BASE_URL_REGION")}{config.get("MATCH", "BY_MATCH_ID")}{match_id}/timeline?api_key={api_key}'
    resp = api_request.make_request(url)
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
            if "timestamp" not in minute:
                print(match_data)
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
    game_duration = get_game_duration(match_data["gameDuration"])
    for player in match_data["participants"]:
        if player["summonerName"] == username:
            if share_team_stat is not None:
                for elem in share_team_stat:
                    player[elem] = player[share_team_stat[elem]] /\
                                   match_data["teams"][int(player["teamId"]/100-1)][share_team_stat[elem]] * 100
            player["goldEfficiency"] = calculate_gold_efficiency(player["goldEarned"],
                                                                 player["totalDamageDealtToChampions"])
            player["csmin"] = (player["totalMinionsKilled"] / game_duration) * 60
            player["visionMinute"] = (player["visionScore"] / game_duration) * 60
            player["damageMinute"] = (player["totalDamageDealtToChampions"] / game_duration) * 60
            player["k+a"] = player["kills"] + player["assists"]
            return player
    return {}


def get_set_data(match_list, player: InputPlayer):
    team_data_list = get_team_data_list()
    player_stats = []
    for match in match_list:
        data = get_match_stats(match, player.getRegion())
        if is_match_valid(data) is True and check_player_position(data, name=player.getUsername(), position=player.getPosition()) is True:
            data_at_15 = get_stats_at_minute(match, 15, player.getRegion())
            team_data = create_team_stats(data, team_data_list)
            match_data = aggregate_data(data, minutes_data=[data_at_15], team_data=team_data)
            player_stats.append(get_player_data(match_data, player.getUsername(), team_data_list))
    return player_stats

def get_match_list(puuid: str, count: int) -> list:
    match_list = get_player_last_games(puuid, count)
    return match_list


def get_champion_list(player_stats: list) -> list:
    champion_list = []
    for game in player_stats:
        if game["championName"] not in champion_list:
            champion_list.append(game["championName"])
    return champion_list


def get_player_stats(player: InputPlayer) -> Player:
    player.setPuuid(get_player_puuid(player))
    match_list = get_player_last_games(player)
    player_stats = get_set_data(match_list, player)
    champion_list = get_champion_list(player_stats)
    specific_data = get_specific_data_list()
    team_data = get_team_data_list()
    at_x_data = get_at_x_data_list()

    player_data = Player(player.getUsername(), team_data, specific_data, at_x_data, champion_list)
    player_data.process_data(player_stats)

    return player_data


def get_players_stats():
    player_list = {
        InputPlayer(username="MiniWolskys", position="MIDDLE", gameCount=10, region="EUW"),
        InputPlayer(username="1Bulgarian", position="MIDDLE", gameCount=10, region="EUNE")
    }

    player_data = {}

    for player in player_list:
        player_data[player.getUsername()] = get_player_stats(player)

    for player in player_data:
        player_data[player].print_data()

    return player_data


def data_to_csv(player_data: dict, writer: csv.writer) -> None:
    for player in player_data:
        data = player_data[player].organize()
        for d in data:
            writer.writerow(d)


def init_csv(f) -> csv.writer:
    writer = csv.writer(f)
    header = ['Player Name / champion', 'games count', '% of team damage', '% of team gold', 'gold efficiency (%)', 'cs/min', 'vision/min', 'damage/min', 'gold@15', 'death@15', 'k+a@15']
    writer.writerow(header)
    return writer


def main():
    with open("results/results.csv", "w", encoding="UTF8", newline="") as f:
        player_data = get_players_stats()
        writer = init_csv(f)
        data_to_csv(player_data, writer)


# Setting up file variables
config = Config()
api_request = APIRequest()

# Getting RIOT API key defined in config.ini
api_key = config.get_api_key()

main()