import json
import random

# TODO: Implement tweet_random
def tweet_random(twitter):
    tweets = ["this", "thing"]

    tweet_text = random.choice(tweets)
    twitter.update_status(status=tweet_text)


def follow_oldest(twitter, redis):
    twitter_id = redis.rpop('queued_follows')

    if twitter_id:
        twitter.create_friendship(user_id=twitter_id)
        print twitter_id + " followed."


def direct_message_oldest(twitter, redis):
    # load dm tuple from json stored in redis
    dm_string = redis.rpop('queued_dms')
    dm = None

    if dm_string:
        dm = tuple(json.loads(dm_string))

    if dm:
        # grab DM info from stored tuple
        twitter_id = dm[0]
        dm_text = dm[1]

        twitter.send_direct_message(user_id=twitter_id, text=dm_text)
        print dm + " sent."


def tweet_oldest(twitter, redis):
    # load tweet tuple from json stored in redis
    tweet_string = redis.rpop('queued_tweets')
    tweet = None

    if tweet_string:
        tweet = tuple(json.loads(tweet_string))

    if tweet:
        tweet_text = tweet[0]
        reply_id = tweet[1]
        twitter.update_status(status=tweet_text, in_reply_to_id=reply_id)
        print "Tweet: "+tweet_text+" was sent."


def retweet_oldest(twitter, redis):
    tweet_id = redis.rpop('queued_retweets')

    if tweet_id:
        twitter.retweet(id=tweet_id)
        print tweet_id + " retweeted."


def fave_oldest(twitter, redis):
    tweet_id = redis.rpop('queued_fave')

    if tweet_id:
        twitter.create_favorite(id=tweet_id)
        print tweet_id + " faved."
