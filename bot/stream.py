import json
import random
from common import redis_init, wordnik_init, BOT_NAME
from twython import TwythonStreamer
from status import generate_emo_status, generate_random_greeting

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


  def on_error(self, status_code, data):
    print status_code


  def _process_dm(self, dm):
    # Don't count direct messages from yourself
    if dm['sender']['name'] is not BOT_NAME:
      print 'Direct message received.'
      self.redis.incr('dms_received')

      message_type = get_message_type(dm['text'])
      self.queue_dm(dm['sender']['id'], message_type=message_type)


  def _process_tweet(self, tweet):
    # reply
    tweet_type = None
    if tweet['in_reply_to_status_id'] is not None:
      tweet_type = "reply"
      self.redis.incr('replies')

      username = tweet['user']['screen_name']
      message_type = get_message_type(tweet['text'])

      if message_type:
        self.queue_tweet(message_type=message_type, reply_to_screenname=username)
      else:
        self.queue_fave(tweet['id'])

    # retweet
    if tweet.has_key('retweeted_status'):
      tweet_type = "retweet"
      self.redis.incr('retweets')
      self.queue_fave(tweet['id'])

    # mention
    if tweet['entities']['user_mentions'] and tweet_type not in ["reply", "retweet"]:
      tweet_type = "mention"
      self.redis.incr('mentions')

      message_type = get_message_type(tweet['text'])
      username = tweet['user']['screen_name']

      # if user is requesting help or an update, give it to them
      if message_type:
        self.queue_tweet(message_type=message_type, reply_to_screenname=username)

      # if not, retweet it
      else:
        self.queue_retweet(tweet['id'])

    print tweet_type + " received."


  def _process_event(self, event):
    print '{0} event received'.format(event['event'])

    # Follow
    if event['event'] == 'follow':
      self.redis.incr('follows')
      user_id = event['source']['id']

      self.queue_follow(user_id)
      self.queue_dm(user_id, response_type='help')

    # Fave
    elif event['event'] == 'favorite' or event['event'] == 'retweet_favorite':
      self.redis.incr('faves')

      username = event['source']['screen_name']
      responses = ["ooooh, @"+username+" is lovin me", "fave fave fave fave fave :D", "ur my fave too, @"+username+"! (:"]

      self.queue_tweet(message_text=random.choice(responses))

    # Unfave
    elif event['event'] == 'unfavorite':
      self.redis.incr('unfaves')
      text = "i'm no longer a fave ;("

      self.queue_tweet(message_text = text)

    # List add
    elif event['event'] == 'list_member_added':
      self.redis.incr('list_adds')

      list_name = event['target_object']['name']
      user_name = event['target_object']['user']['screen_name']
      text = ":D I got added to "+list_name+"! thanks @"+username+" !!"

      self.queue_tweet(message_text=text)

    # List remove
    elif event['event'] == 'list_member_removed':
      self.redis.incr('list_removes')

      list_name = "unknown"
      text = ":( somebody removed me from "+list_name+" :( :("

      self.queue_tweet(message_text=text)

  def queue_dm(self, user_id, message_text=None, message_type=None):

    if message_type == 'help':
      message_text = "hiii i love new friends!! fave for fave? or maybe ask me how I'm doing?"

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

    print "FOLLOW QUEUED: "+ user_id


  def queue_fave(self, tweet_id):
    self.redis.lpush('queued_faves', tweet_id)

    print "FAVE QUEUED: "+ tweet_id


  def queue_tweet(self, message_text=None, reply_to_screenname=None, message_type=None):
    if message_type == 'help':
      message_text = "i love new friends!! fave for fave? or maybe ask me how I'm doing?"
    elif message_type == 'status':
      message_text = generate_emo_status(self.redis, self.wordApi)
    else:
      if not message_text:
        message_text = generate_random_greeting()
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
  status_phrases = ['how are u','how are you',"what's up",'whats up','wut up','wat ^','status','how u doin']

  if help in message_text:
    return 'help'
  else:
    for phrase in status_phrases:
      if phrase in message_text:
        return 'status'
    return None
