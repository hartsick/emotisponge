import twitter
import os
import redis

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

    # for each dm, reply & increment counter
    num_dms = 0
    for dm in most_recent_dms:
        send_dm_response(dm)
        num_dms += 1

    # update index
    redis.set('dm:since_id:last', most_recent_dms[0].id)

    return num_dms

def send_dm_response(dm):
    twitter.PostDirectMessage("ur the sweetest, thx (:", dm.sender_id)

def check_faves():
    pass

# def check_follows():

# def check_mentions():

# def check_replies():

# def check_retweets():

# def check_timeout():

# Rev the engines
twitter = twit_init()
redis = redis_init()

# Get going
while True:
    num_dms = check_dms()

    # faves = check_faves()
    # print faves

    # follows = check_follows()
    # print follows

    # mentions = check_mentions()
    # print mentions

    # replies = check_replies()
    # print replies

    # retweets = check_retweets()
    # print retweets

    # timeout = check_timeout()
    # print timeout


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
