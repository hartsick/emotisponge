import os
from twython import Twython
from bot.common import redis_init, twitter_credentials_init
from bot.age import set_birth_time

if __name__ == '__main__':

    # Redis & Twitter init
    redis = redis_init()
    twitter = Twython(*twitter_credentials_init())

    # A bby is born
    set_birth_time(redis=redis, twitter=twitter)
