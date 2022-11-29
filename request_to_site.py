import requests
from config import URL


class SendRequest:

    def send_request(self, url_append=""):
        response = requests.get(URL + url_append)
        return response.text


sendreq = SendRequest()
