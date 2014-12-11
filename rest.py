from twython import Twython
from common import twitter_auth_credentials, redis, REDIS_KEYS
import json

twitter = Twython(*twitter_auth_credentials)

def follow_oldest():
    twitter_id = redis.rpop('queued_follows')

    if twitter_id:
        twitter.create_friendship(user_id=twitter_id)
        print twitter_id + " followed."

def direct_message_oldest():
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

def tweet_oldest():
    # load tweet tuple from json stored in redis
    tweet_string = redis.rpop('queued_tweets')
    tweet = None

    if tweet_string:
        tweet = tuple(json.loads(tweet_string))

    if tweet:
        tweet_text = tweet[0]
        reply_id = tweet[1]
        twitter.update_status(status=tweet_text, in_reply_to_id=reply_id)

follow_oldest()
direct_message_oldest()
# tweet_oldest()
