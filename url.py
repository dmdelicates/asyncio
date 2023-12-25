import requests

URL1 = 'https://swapi.dev/'
URL2 = 'https://www.swapi.tech/'


def check_url(url1):
    response = requests.get(url1)
    if response.ok:
        return url1
    return False


URL = check_url(URL1)
