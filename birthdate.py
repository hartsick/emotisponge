from datetime import datetime
import json
from common import redis, REDIS_KEYS
import dateutil.parser as parser
from rest import twitter

def set_birth_day():
    current_time = datetime.now()

    # Redis stores strings, so convert accordingly
    time_as_string = current_time.isoformat()
    redis.set('birth_date', time_as_string)

    human_readable_time = datetime.strftime(current_time,'%a, %B %d, %Y at %X %Z')

    print "An emotisponge was born at " + human_readable_time + "!"
    # twitter.update_status(status="An emotisponge was born at " + human_readable_time + "!")

def get_birth_day():
    string = redis.get('birth_date')
    date = parser.parse(string)

    return date
