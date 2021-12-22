import os
from configparser import ConfigParser

class Config:

    def __init__(self):
        self.config = ConfigParser()
        path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
        self.config.read(os.path.join(path, 'config.ini'))

    def read_api_key(self) -> str:
        if "CORE" in self.config and "ApiKey" in self.config["CORE"]:
            return self.config["CORE"]["ApiKey"]
        return ""

    def get_api_key(self) -> str:
        api_key = self.read_api_key()
        if api_key == "":
            raise Exception("API Key is not defined. Please add it to the config.ini file, or pass it as argument.")
        return api_key

    def get(self, main, second) -> str:
        if main not in self.config or second not in self.config[main]:
            raise Exception(f"{second} is not defined in {main} or {main} is not defined in config file.")
        return self.config[main][second]
