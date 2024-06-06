import yaml
from requests_oauthlib import OAuth1Session

config = yaml.safe_load(open("config_empty.yaml"))

consumer_key = config['KEYS']['immoKey']
consumer_secret = config['KEYS']['immoSecret']

oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
url = 'https://rest.sandbox-immobilienscout24.de/restapi/api/gis/v1.0/country/276/region'

response = oauth.get(url)

if response.status_code == 200:
    print(response.text)
