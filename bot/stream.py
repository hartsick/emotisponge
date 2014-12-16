import json
import random
from common import redis_init, wordnik_init, BOT_NAME, BOT_ID
from twython import TwythonStreamer
from status import generate_emo_status, generate_random_greeting, HELP_TEXT

class TweetStreamer(TwythonStreamer):

  def __init__(self, *args, **kwargs):
    self.redis = redis_init()
    self.wordApi = wordnik_init()
    TwythonStreamer.__init__(self, *args, **kwargs)

  def on_success(self, data):
    if data.get('direct_message'):
      self._process_dm(data['direct_message'])
    elif data.get('text'):
      self._process_tweet(data)
    elif data.get('event'):
      self._process_event(data)

    print "data received:"
    print data


  def on_error(self, status_code, data):
    print "Error: {0}".format(status_code)


  def _process_dm(self, dm):
    # Don't count direct messages from yourself
    if dm['sender']['name'] is not BOT_NAME:
      print 'Direct message received.'
      self.redis.incr('dms_received')

      message_type = get_message_type(dm['text'])
      self.queue_dm(dm['sender']['id'], message_type=message_type)


  def _process_tweet(self, tweet):
    tweet_type = None

    # reply
    if tweet['in_reply_to_status_id'] is not None:
      tweet_type = "reply"

      # Ignore own replies
      if tweet['user']['name'] is not BOT_NAME:
        self.redis.incr('replies')

        username = tweet['user']['name']
        message_type = get_message_type(tweet['text'])

        if message_type:
          self.queue_tweet(message_type=message_type, reply_to_screenname=username)
        else:
          self.queue_fave(tweet['id'])

    # retweet
    if tweet.has_key('retweeted_status'):
      tweet_type = "retweet"

      # Ignore own retweets
      RT_prefix_template = "RT @{0}".format(BOT_NAME)
      tweet_prefix = tweet['text'].split(':')[0]

      if tweet_prefix is not RT_prefix_template:
        self.redis.incr('retweets')
        self.queue_fave(tweet['id'])

    # mention
    if tweet['entities']['user_mentions'] and tweet_type not in ["reply", "retweet"]:
      tweet_type = "mention"

      # Ignore self-mentions
      if tweet['user']['name'] is not BOT_NAME:
        self.redis.incr('mentions')

        message_type = get_message_type(tweet['text'])
        username = tweet['user']['name']

        # if user is requesting help or an update, give it to them
        if message_type:
          self.queue_tweet(message_type=message_type, reply_to_screenname=username)

        # otherwise...
        else:
          # if mention, RT
          if "@{0}".format(BOT_NAME) not in tweet['text'].split(' ')[0]:
            self.queue_retweet(tweet['id'])

          # otherwise, just respond
          self.queue_tweet(reply_to_screenname=username)


        print tweet_type + " received."


  def _process_event(self, event):
    print '{0} event received'.format(event['event'])

    source_id =   event['source']['id']
    source_name = event['source']['name']

    # Fave
    if event['event'] == 'favorite':

      # Ignore bot-triggered events
      if source_name is not BOT_NAME:
        self.redis.incr('faves')

        responses = ["ooooh, @"+source_name+" is lovin me", "fave fave fave fave fave :D", "ur my fave too, @"+source_name+"! (:"]

        self.queue_tweet(message_text=random.choice(responses))

    # Unfave
    elif event['event'] == 'unfavorite':

      # Ignore bot-triggered events
      if source_id is not BOT_ID:
        self.redis.incr('unfaves')
        text = "i'm no longer a fave ;("

        self.queue_tweet(message_text = text)

    # Follow
    elif event['event'] == 'follow':

      # Ignore bot-triggered events
      if source_id is not BOT_ID:

        self.redis.incr('follows')

        self.queue_follow(source_id)
        self.queue_dm(source_id, message_type='help')

    # List add
    elif event['event'] == 'list_member_added':
      self.redis.incr('list_adds')

      list_name = event['target_object']['name']
      user_name = event['target_object']['user']['name']
      text = ":D I got added to "+list_name+"! thanks @"+user_name+" !!"

      self.queue_tweet(message_text=text)

    # List remove
    elif event['event'] == 'list_member_removed':
      self.redis.incr('list_removes')

      list_name = "unknown"
      text = ":( somebody removed me from a list :( :("

      self.queue_tweet(message_text=text)


  def queue_dm(self, user_id, message_text=None, message_type=None):
    # annoying hack to prevent self-reply loop
    # TODO: fix
    if user_id == BOT_ID:
      pass
    else:
      if message_type == 'help':
        message_text = HELP_TEXT

      elif message_type == 'status':
        message_text = generate_emo_status(self.redis, self.wordApi)

      if not message_text:
        sentence_options = ["thx for the message! i'm just a lil ol bot and don't know many words", "<(^.^)>", "whats up pup", "pbbbbbbbbbt", "i like talking to u", "sorry, i don't talk much, but i like to listen", "tweet tweet", "In another life, I was aboard Apollo 11 and now I have been reduced to this."]

        message_text = random.choice(sentence_options)

      # prepare dm tuple for storage
      dm_store = json.dumps((user_id, message_text))
      self.redis.lpush('queued_dms', dm_store)

      print "DM QUEUED: "+ message_text


  def queue_follow(self, user_id):
    self.redis.lpush('queued_follows', user_id)

    print "FOLLOW QUEUED: {0}".format(user_id)


  def queue_fave(self, tweet_id):
    self.redis.lpush('queued_faves', tweet_id)

    print "FAVE QUEUED: {0}".format(tweet_id)


  def queue_tweet(self, message_text=None, reply_to_screenname=None, message_type=None):
    # annoying hack to prevent self-reply loop
    if reply_to_screenname == BOT_NAME:
      pass

    else:
      # respond to help
      if message_type == 'help':
        message_text = HELP_TEXT

      # respond to status
      elif message_type == 'status':
        message_text = generate_emo_status(self.redis, self.wordApi)

      else:
        # if no message text, generate it yourself
        if not message_text:
          message_text = generate_random_greeting()

      # if reply, manually prepend the person to reply to
      if reply_to_screenname:
        message_text = '@{0} {1}'.format(reply_to_screenname, message_text)

      self.redis.lpush('queued_tweets', message_text)

      print "TWEET QUEUED: "+ message_text


  def queue_retweet(self, tweet_id):
    self.redis.lpush('queued_retweets', tweet_id)

    print "RETWEET QUEUED: {0}".format(tweet_id)


# Begin helper functions

def get_message_type(message_text):
  help = 'help'
  status_phrases = ['how are u','how are you','whats up','wut up','wat ^','status','how u doin','hows it goin']

  # convert message text to lowercase without apostrophes
  lower_text = message_text.lower().replace("'","")

  if help in lower_text:
    return 'help'
  else:
    for phrase in status_phrases:
      if phrase in lower_text:
        return 'status'
    return None
