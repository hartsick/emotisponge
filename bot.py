import twitter
import os
import redis
import random

def twit_init():
    consumer_key = os.environ.get('EMOTISPONGE_CONSUMER_KEY')
    consumer_secret = os.environ.get('EMOTISPONGE_CONSUMER_SECRET')
    access_token = os.environ.get('EMOTISPONGE_ACCESS_TOKEN')
    access_token_secret = os.environ.get('EMOTISPONGE_ACCESS_TOKEN_SECRET')

    api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)

    return api

def redis_init():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)

    return r

def check_dms():
    # check for any dms received since last run
    last_dm_id = redis.get('dm:since_id:last')
    most_recent_dms = twitter.GetDirectMessages(last_dm_id)

    # update index, if needed
    if most_recent_dms:
        redis.set('dm:since_id:last', most_recent_dms[0].id)

    # for each dm, reply & increment counter
    num_dms = 0
    for dm in most_recent_dms:
        send_dm_response(dm.sender_id)
        num_dms += 1

    return num_dms

def send_dm_response(id, text=None):
    index = 0
    if text is None:
        possible_dms = [
            "ur the sweetest, thx (:",
            "(: aw shucks",
            "yea yea yea",

        ]
        text = possible_dms[index]
        index += 1
    twitter.PostDirectMessage(text, id)

def check_faves():
    pass

def check_follows():
    # check for any follows received since last run
    current_followers = set(twitter.GetFollowerIDs())
    past_followers = redis.smembers('follower_ids')
    new_followers = current_followers.difference(past_followers)

    # follow back & send a message with instructions
    if new_followers:

        for fid in new_followers:
            twitter.CreateFriendship(fid)

            message = "thx 4 the follow!! if u have any questions just reply 2me and say 'help', ok?/?"
            send_dm_response(fid, message)

            redis.sadd('follower_ids', fid)


def follow_back(follow):
    pass

def check_mentions():
    pass

def check_replies():
    pass

def check_retweets():
    pass

# Rev the engines
twitter = twit_init()
redis = redis_init()

# Get going
while True:
    num_follows     = check_follows()
    num_dms         = check_dms()
    num_faves       = check_faves()
    num_mentions    = check_mentions()
    num_replies     = check_replies()
    num_retweets    = check_retweets()

# check for rate limit, set timer
# respond to action with appropriate message
# increment life counter
# if below 0, die.


# Interesting methods:
    # GetFavorites  (max 20)
        # since_id:

    # GetFollowerIDs (max 5000)
    # GetMentions  (max 20)
        # since_id:
    # GetReplies (max 20)
        # since_id
    # GetRetweetsOfMe (max 100)
        # since_id
    # GetSleepTime

    # PostRetweet
    # PostUpdate
    # PostUpdates
