import time
from datetime import datetime
import os
import logging
from multiprocessing import Process
from twython import Twython
from bot.stream import TweetStreamer
from bot.common import redis_init, twitter_credentials_init
import bot.rest as rest


def run_stream():
    # Start Twitter stream, restart with delay on exception
    while True:
        try:
            stream = TweetStreamer(*twitter_credentials_init())
            stream.user(**{'with': 'user'})
        except Exception as e:
            logging.exception(e)

        time.sleep(30)


def process_queue():
    redis = redis_init()
    twitter = Twython(*twitter_credentials_init())

    # TODO: Properly rate limit calls
    while True:
        print "Processing queue..."
        print datetime.utcnow()
        try:
            rest.follow_oldest(twitter, redis)
            rest.direct_message_oldest(twitter, redis)
            rest.tweet_oldest(twitter, redis)
            rest.retweet_oldest(twitter, redis)
            rest.fave_oldest(twitter, redis)
        except Exception as e:
            logging.exception(e)

        time.sleep(60)


if __name__ == "__main__":

    p1 = Process(target=run_stream)
    p2 = Process(target=process_queue)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
