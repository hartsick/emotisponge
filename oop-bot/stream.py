from common import twitter_auth
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.models import Status, DirectMessage

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_connect(self):
        print "Listening..."

    def on_error(self, status):
        print(status)

    def on_direct_message(self, status):
        print "DM:"
        print type(status)
        print(status)

    def on_event(self, status):
        print "Event:"
        print type(status)
        print(status)

    def on_status(self, status):
        print "Status:"
        print type(status)
        print(status)


l = StdOutListener()
auth = OAuthHandler(twitter_auth['consumer_key'], twitter_auth['consumer_secret'])
auth.set_access_token(twitter_auth['access_token'], twitter_auth['access_token_secret'])

stream = Stream(auth, l)
stream.userstream( _with='user' )
