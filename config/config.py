from configparser import ConfigParser


def read_api_key() -> str:
    config = ConfigParser()
    config.read('../config/config.ini')
    if "CORE" in config and "ApiKey" in config["CORE"]:
        return config["CORE"]["ApiKey"]
    return ""


def get_api_key() -> str:
    api_key = read_api_key()
    if api_key == "":
        raise Exception("API Key is not defined. Please add it to the config.ini file, or pass it as argument.")
    return api_key
