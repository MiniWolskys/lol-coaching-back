import requests
import time

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
