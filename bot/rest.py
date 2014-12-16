import json
import random

# TODO: Implement tweet_random
def tweet_random(twitter):
    tweets = ["this", "thing"]

    tweet_text = random.choice(tweets)
    twitter.update_status(status=tweet_text)

    return True


def follow_oldest(twitter, redis):
    twitter_id = redis.rpop('queued_follows')
    print "follow_oldest: {0}".format(twitter_id)

    if twitter_id:
        twitter.create_friendship(user_id=twitter_id)

        print "FOLLOW SENT: {0}".format(twitter_id)
        return True


def direct_message_oldest(twitter, redis):
    # load dm tuple from json stored in redis
    dm_string = redis.rpop('queued_dms')
    dm = None

    print "dm_oldest: {0}".format(dm_string)

    if dm_string:
        dm = tuple(json.loads(dm_string))

    if dm:
        # grab DM info from stored tuple
        twitter_id = dm[0]
        dm_text = dm[1]

        twitter.send_direct_message(user_id=twitter_id, text=dm_text)

        print "DM SENT: " +dm[1]
        return True


def tweet_oldest(twitter, redis):
    tweet_text = redis.rpop('queued_tweets')

    print "tweet_oldest: {0}".format(tweet_text)

    if tweet_text:
        twitter.update_status(status=tweet_text)

        print "TWEET SENT: "+tweet_text
        return True


def retweet_oldest(twitter, redis):
    tweet_id_string = redis.rpop('queued_retweets')

    print "retweet_oldest: {0}".format(tweet_id_string)

    if tweet_id_string:
        tweet_id = int(tweet_id_string)
        twitter.retweet(id=tweet_id)

        print "RT SENT: {0}".format(tweet_id)
        return True


def fave_oldest(twitter, redis):
    tweet_id_string = redis.rpop('queued_fave')
    print "fave_oldest: {0}".format(tweet_id)

    if tweet_id_string:
        tweet_id = int(tweet_id_string)
        twitter.create_favorite(id=tweet_id)

        print "FAVE SENT: {0}".format(tweet_id)
        return True


def get_rate_limit(twitter):
    print "GET RATE LIMIT"

    num_remaining = twitter.get_lastfunction_header('x-rate-limit-remaining')

    time_remaining = None
    if num_remaining <= 0:
        reset = twitter.get_lastfunction_header('x-rate-limit-reset')

        current_time = int(time())
        time_remaining = reset_time - current_time

    rate_limit = { 'remaining': num_remaining, 'time_until_reset': time_remaining }

    print "{0} posts remaining. Reset in {1}".format(num_remaining, time_remaining)
    return rate_limit
