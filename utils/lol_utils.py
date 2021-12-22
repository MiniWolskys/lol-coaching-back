from configuration.config import Config
from utils.utils import APIRequest


class InputPlayer:
    def __init__(self, username:str, region:str, gameCount:int=1, position:str='') -> None:
        self.username = username
        self.region = region
        self.gameCount = gameCount
        self.position = position
        self.puuid = ''

    def setPuuid(self, puuid: str) -> None:
        self.puuid = puuid

    def getPuuid(self) -> str:
        return self.puuid

    def getUsername(self) -> str:
        return self.username

    def getRegion(self) -> str:
        return self.region

    def getPosition(self) -> str:
        return self.position

    def getGameCount(self) -> int:
        return self.gameCount


class LoL:
    def __init__(self) -> None:
        self.config = Config()
        self.api_key = self.config.get_api_key()
        self.api_request = APIRequest()

    def get_player_puuid(self, player: InputPlayer) -> str:
        url = f'{self.config.get(player.getRegion(), "BASE_URL_PLATFORM")}{self.config.get("SUMMONER", "BY_NAME")}{player.getUsername()}?api_key={self.api_key}'
        resp = self.api_request.make_request(url)
        data = resp.json()
        if "puuid" not in data:
            raise Exception(f"No user found for username {player.getUsername()}, check API KEY is still valid and user is correct.")
        puuid = data["puuid"]
        return puuid

    def get_player_last_games(self, player: InputPlayer) -> list:
        url = f'{self.config.get(player.getRegion(), "BASE_URL_REGION")}{self.config.get("MATCH", "BY_PUUID")}{player.getPuuid()}/ids?start=0&count={player.getGameCount()}&api_key={self.api_key}'
        resp = self.api_request.make_request(url)
        match_list = resp.json()
        return match_list

    def get_match_stats(self, match_id: str, region: str) -> dict:
        url = f'{self.config.get(region, "BASE_URL_REGION")}{self.config.get("MATCH", "BY_MATCH_ID")}{match_id}?api_key={self.api_key}'
        resp = self.api_request.make_request(url)
        data_json = resp.json()
        if "info" not in data_json:
            raise Exception(f"No information retrieved for match {match_id}")
        data = data_json["info"]
        return data

    def get_stats_at_minute(self, match_id: str, minute: int, region: str) -> dict:
        url = f'{self.config.get(region, "BASE_URL_REGION")}{self.config.get("MATCH", "BY_MATCH_ID")}{match_id}/timeline?api_key={self.api_key}'
        resp = self.api_request.make_request(url)
        data_json = resp.json()
        if "info" not in data_json:
            raise Exception(f"No information retrieved for match {match_id}")
        data = data_json["info"]
        data = self.get_extra_data_at_minute(data, minute)
        for frame in data["frames"]:
            if 60000 * (minute + 1) > frame["timestamp"] > 60000 * minute:
                return {"timestamp": frame["timestamp"], "data": frame["participantFrames"]}
        return {}

    def get_extra_data_at_minute(self, data: dict, minute: int) -> dict:
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
