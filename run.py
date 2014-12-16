import time
from datetime import datetime
import os
import logging
from multiprocessing import Process, Pool
from twython import Twython
from bot.stream import TweetStreamer
from bot.common import redis_init, twitter_credentials_init
import bot.rest as rest

# TODO: Periodically tweet random things, not above rate limit
# TODO: Perodically check score and kill bot

def run_stream():
    # Start Twitter stream, restart with delay on crash
    while True:
        try:
            stream = TweetStreamer(*twitter_credentials_init())
            stream.user(**{'with': 'user'})
        except Exception as e:
            logging.exception(e)

        time.sleep(60)


def process_queues(rest_function):
    print rest_function
    redis = redis_init()
    twitter = Twython(*twitter_credentials_init())

    while True:
        try:
            sent = rest_function(twitter, redis)
            print "sent is {0}".format(sent)

            if sent is True:
                print "action taken. calculating rate_limit"
                rate_limit = rest.get_rate_limit(twitter)

                # If rate limit exhausted, wait until refreshed
                if rate_limit['time_until_reset']:
                    time.sleep(rate_limit['time_until_reset'])

        except Exception as e:
            logging.exception(e)

        time.sleep(5)


if __name__ == "__main__":

    # TODO: add tweet_random
    rest_functions = [rest.follow_oldest, rest.direct_message_oldest, rest.tweet_oldest, rest.retweet_oldest, rest.fave_oldest]

    p1 = Process(target=run_stream)

    processes = [p1]
    for func in rest_functions:
        p = Process(target=process_queues, args=(func,))
        processes.append(p)

    # Start all processes, then join
    for p in processes:
        p.start()

    for p in processes:
        p.join()
