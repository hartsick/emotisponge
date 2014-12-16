import os
import redis
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi

# Bot info
BOT_NAME = 'emotisponge'
BOT_ID = 2921127146

# Weights for determining Score
EVENT_VALUES = {
'follows': 4, 'list_adds': 5, 'list_removes': -5, 'dms_received': 1, 'dms_sent': 0,
'mentions': 3, 'replies':2, 'faves': 1, 'unfaves': -1, 'retweets': 2
}
EVENT_NAMES = EVENT_VALUES.keys()
AGE_WEIGHT = 4

def twitter_credentials_init():
  consumer_key = os.environ.get('EMOTISPONGE_CONSUMER_KEY')
  consumer_secret = os.environ.get('EMOTISPONGE_CONSUMER_SECRET')
  access_token = os.environ.get('EMOTISPONGE_ACCESS_TOKEN')
  access_token_secret = os.environ.get('EMOTISPONGE_ACCESS_TOKEN_SECRET')

  credentials = (   consumer_key,
                    consumer_secret,
                    access_token,
                    access_token_secret)

  return credentials


def redis_init():
  redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
  r = redis.from_url(redis_url)

  # initialize event counters to 0 if unset
  for event_name in EVENT_NAMES:
    r.setnx(event_name, 0)

  return r


def wordnik_init():
  apiUrl = 'http://api.wordnik.com/v4'
  apiKey = os.environ.get('EMOTISPONGE_WORDNIK_KEY')
  client = ApiClient(apiKey, apiUrl)

  wordApi = WordApi(client)

  return wordApi
