import os
import redis

REDIS_KEYS = ['follows', 'list_adds', 'list_removes', 'dms_received', 'dms_sent', 'mentions', 'replies', 'faves', 'unfaves', 'retweets' ]

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

  return r

redis = redis_init()
twitter_auth_credentials = twitter_credentials_init()
