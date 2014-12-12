import os
from twython import Twython
from common import redis_init, twitter_credentials_init
from age import set_birth_time

if __name__ == '__main__':

    # Redis & Twitter init
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)

    twitter = Twython(*twitter_credentials_init)

    # A bby is born
    set_birth_time(redis=r, twitter=twitter)
