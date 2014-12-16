import time
from datetime import datetime
import os
import logging
from multiprocessing import Process
from twython import Twython
from bot.stream import TweetStreamer
from bot.common import redis_init, twitter_credentials_init
import bot.rest as rest

# TODO: Periodically tweet random things, not above rate limit
# TODO: Perodically check score and kill bot

def run_stream():
    # start Twitter stream, restart with delay on crash
    while True:
        try:
            stream = TweetStreamer(*twitter_credentials_init())
            stream.user(**{'with': 'user'})
        except Exception as e:
            logging.exception(e)

        time.sleep(60)


def process_queues(rest_function, redis, twitter):

    while True:
        try:
            sent = rest_function(twitter, redis)

            if sent is True:
                print "action taken. calculating rate limit"
                rate_limit = rest.get_rate_limit(twitter)

                # If rate limit exhausted, wait until refreshed
                if rate_limit['time_until_reset']:
                    time.sleep(rate_limit['time_until_reset'])

                time.sleep(5)

        except Exception as e:
            logging.exception(e)


if __name__ == "__main__":

    redis = redis_init()
    twitter = Twython(*twitter_credentials_init())

    # TODO: add tweet_random
    rest_functions = [rest.follow_oldest, rest.direct_message_oldest, rest.tweet_oldest, rest.retweet_oldest, rest.fave_oldest]

    p1 = Process(target=run_stream)

    processes = [p1]
    for func in rest_functions:
        # use one redis & twitter connection
        p = Process(target=process_queues, args=(func, redis, twitter))
        processes.append(p)

    # Start all processes, then join
    for p in processes:
        p.start()

    for p in processes:
        p.join()
