import logging
from twython import TwythonStreamer
from common import redis, twitter_auth_credentials
import rest
import random
import json
from status import *

class TweetStreamer(TwythonStreamer):

  def on_success(self,data):
    if data.get('direct_message'):
      _process_dm(data['direct_message'])
    elif data.get('text'):
      _process_tweet(data)
    elif data.get('event'):
      _process_event(data)

    # check emo score, shut it down if dead

  def on_error(self, status_code, data):
    print status_code


def _process_dm(dm):

  print 'Direct message received.'
  redis.incr('dms_received')

  response_type = 'status' if ('how are u' or 'how are you' or "what's up" or 'whats up' or 'wut up' or 'status' or 'how u doin') in dm['text'] else None
  response_type = 'help' if 'help' in dm['text'] else None

  queue_dm(dm['sender']['id'], response_type=response_type)


def _process_tweet(tweet):
  # reply
  if tweet['in_reply_to_status_id'] is not None:
    redis.incr('replies')
    # tweet_response(tweet)

  # retweet
  if tweet['retweeted_status'] is not None:
    redis.incr('retweets')
    print "Retweet received."

  # mention
  if tweet['entities']['user_mentions']:
    redis.incr('mentions')
    # tweet_response(tweet)


def _process_event(event):
  print '{0} event received'.format(event['event'])

  if event['event'] == 'follow':
    redis.incr('follows')
    user_id = event['source']['id']
    queue_follow(user_id)
    queue_dm(user_id, response_type='help')

  elif event['event'] == 'favorite':
    redis.incr('faves')
    # tweet happiness

  elif event['event'] == 'unfavorite':
    redis.incr('unfaves')
    # tweet sadness?

  elif event['event'] == 'list_member_added':
    redis.incr('list_adds')
    # tweet about the list

  elif event['event'] == 'list_member_removed':
    redis.incr('list_removes')
    # tweet sadness


def queue_dm(user_id, message_text=None, response_type=None):

  if response_type == 'help':
    message_text = "hiii i love new friends!! fave for fave? or maybe ask me how I'm doing?"

  elif response_type == 'status':
    message_text = generate_emo_status()

  if not message_text:
    tweets = ["some", "random", "options"]
    message_text = random.choice(tweets)

  # prepare dm tuple for storage
  dm_store = json.dumps((user_id, message_text))
  redis.lpush('queued_dms', dm_store)


def queue_follow(user_id):
  redis.lpush('queued_follows', user_id)

def queue_tweet(message_text, screenname=None):
  if 'help' in message_text:
    message_text = "i love new friends!! fave for fave? or maybe ask me how I'm doing?"
  if ('how are u' or 'how are you' or "what's up" or 'whats up' or 'wut up' or 'status' or 'how u doin') in message_text:
    message_text = generate_emo_status()
  if not message_text:
    message_text = generate_random_greeting()
  if screenname:
    message_text = '@{0} {1}'.format(screenname, message_text)
    redis.lpush('queued_tweets', message_text)


stream = TweetStreamer(*twitter_auth_credentials)
stream.user(**{'with': 'user'})
