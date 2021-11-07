import os
from configparser import ConfigParser

def read_api_key() -> str:
    config = ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config.read(os.path.join(path, 'config.ini'))
    if "CORE" in config and "ApiKey" in config["CORE"]:
        return config["CORE"]["ApiKey"]
    return ""


def get_api_key() -> str:
    api_key = read_api_key()
    if api_key == "":
        raise Exception("API Key is not defined. Please add it to the config.ini file, or pass it as argument.")
    return api_key
