from twython import Twython
from common import twitter_auth, redis, KEYS

twitter = Twython(*twitter_auth)


def process_queues():
  rates = twitter.get_application_rate_limit_status()
  # TODO: Create periodic processes for queues
  # twitter.update_status(status=message_text)
