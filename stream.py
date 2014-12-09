import logging
from twython import TwythonStreamer
from common import redis, twitter_auth, KEYS
import rest
import random

class TweetStreamer(TwythonStreamer):

  def on_success(self,data):
    if data.get('direct_message'):
      _process_dm(data['direct_message'])
    elif data.get('text'):
      _process_tweet(data)
    elif data.get('event'):
      _process_event(data)

    print data
    check_score()

  def on_error(self, status_code, data):
    print status_code


def _process_dm(dm):
  print 'Direct message received.'
  redis.incr('dms_received')
  response_type = 'status' if ('how are u' or 'how are you' or "what's up" or 'whats up' or 'wut up' or 'status' or 'how u doin') in dm['text'] else None
  response_type = 'help' if 'help' in dm['text'] else None
  queue_dm_response(dm['sender']['id'], response_type=response_type)

def queue_dm_response(user_id, message_text=None, response_type=None):
  if response_type == 'help':
    message_text = "i love new friends!! fave for fave? or maybe ask me how I'm doing?"
  elif response_type == 'status':
    print "calculate status"
  if not message_text:
    tweets = ["some", "random", "options"]
    message_text = random.choice(tweets)
  print "send '{0}' to {1}".format(message_text, user_id)
  redis.lpush('queued_dms', (user_id, message_text))

def send_dms():
  pass

def _process_tweet(tweet):
  print 'Tweet received.'
  print tweet
  # determine type of tweet
  # increment redis db
  # queue tweet response
    # if 'help', return directions
    # if not, return greeting

def _process_event(event):
  print '{0} event received'.format(event['event'])

  if event['event'] == 'follow':
    redis.incr('follows')
    # increment counter
    # follow back
    # dm with info
  elif event['event'] == 'favorite':
    redis.incr('faves')
    # increment counter
    # tweet happiness
  elif event['event'] == 'unfavorite':
    redis.incr('unfaves')
    # incremet counter
    # tweet sadness?
  elif event['event'] == 'list_member_added':
    redis.incr('list_adds')
    # increment counter
    # tweet about the list
  elif event['event'] == 'list_member_removed':
    redis.incr('list_removes')
    # decrement counter
    # tweet sadness

def queue_tweet(message_text, screenname=None):
  # if not message_text:
    # print "queuing tweet failed. please provide message text"
  if screenname:
    message_text = '@{0} {1}'.format(screenname, message_text)
    redis.lpush('queued_tweets', message_text)

def check_score():
  values = redis.mget(*KEYS)
  print values

stream = TweetStreamer(*twitter_auth)
stream.user(**{'with': 'user'})
