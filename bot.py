import twitter
import os
import redis

def twit_init():
    # Load environment variables
    consumer_key = os.environ.get('EMOTISPONGE_CONSUMER_KEY')
    consumer_secret = os.environ.get('EMOTISPONGE_CONSUMER_SECRET')
    access_token = os.environ.get('EMOTISPONGE_ACCESS_TOKEN')
    access_token_secret = os.environ.get('EMOTISPONGE_ACCESS_TOKEN_SECRET')

    # Twitter Init
    api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)

    return api

def redis_init():

    # Redis Init
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)

    return r

twitter = twit_init()
twitter.PostUpdate("luv me")
