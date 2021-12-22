from configuration.config import Config
from utils import APIRequest

def get_game_duration(time_t: int) -> int:
    if time_t < 15000:
        return time_t
    return int(time_t / 1000)

def is_match_valid(match_stat: dict) -> bool:
    if match_stat["mapId"] == 11 and match_stat["gameMode"] == "CLASSIC" and match_stat["gameType"] == "MATCHED_GAME"\
            and get_game_duration(match_stat["gameDuration"]) > 900:
        return True
    return False

def get_last_game(puuid: str, region: str) -> str:
    url = f'{config.get(region, "BASE_URL_REGION")}{config.get("MATCH", "BY_PUUID")}{puuid}/ids?start=0&count=1&api_key={api_key}'
    resp = api_request.make_request(url)
    match = resp.json()[0]
    return match

def get_player_puuid(username: str, region: str) -> str:
    url = f'{config.get(region, "BASE_URL_PLATFORM")}{config.get("SUMMONER", "BY_NAME")}{username}?api_key={api_key}'
    resp = api_request.make_request(url)
    data = resp.json()
    if "puuid" not in data:
        raise Exception(f"No user found for username {username}, check API KEY is still valid and user is correct.")
    puuid = data["puuid"]
    return puuid

def get_match_data(last_game: str, region: str) -> dict:
    url = f'{config.get(region, "BASE_URL_REGION")}{config.get("MATCH", "BY_MATCH_ID")}{last_game}?api_key={api_key}'
    resp = api_request.make_request(url)
    data_json = resp.json()
    if "info" not in data_json:
        raise Exception(f"No information retrieved for match {last_game}")
    data = data_json["info"]
    return data

def get_game_data(last_game: str, region: str) -> dict:
    data = get_match_data(last_game, region)
    if is_match_valid(data) == False:
        return {}
    return data

def main():
    puuid = get_player_puuid(username, region)
    last_game = get_last_game(puuid, region)
    game_data = get_game_data(last_game, region)
    print(game_data)


username = "MiniWolskys"
region = "EUW"

config = Config()
api_request = APIRequest()

api_key = config.get_api_key()

main()