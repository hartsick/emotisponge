import time
from stream import TweetStreamer
from common import twitter_credentials_init


def run_stream():
    # Start Twitter stream, restart with delay on exception
    while True:
        try:
            stream = TweetStreamer(*twitter_credentials_init())
            stream.user(**{'with': 'user'})
        except Exception as e:
            print e

        time.sleep(30)


if __name__ == "__main__":
    run_stream()
