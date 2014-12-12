import json
from datetime import datetime
import dateutil.parser as parser
from common import redis, AGE_WEIGHT
from rest import twitter

def set_birth_time():
    current_time = datetime.now()

    # Redis stores strings, so convert accordingly
    time_as_string = current_time.isoformat()
    redis.set('birth_date', time_as_string)

    human_readable_time = datetime.strftime(current_time,'%a, %B %d, %Y at %X %Z')

    print "An emotisponge was born at " + human_readable_time + "!"
    # twitter.update_status(status="An emotisponge was born at " + human_readable_time + "!")

def get_birth_time():
    string = redis.get('birth_date')
    date = parser.parse(string)

    return date

def age():
    age = datetime.now() - get_birth_time()
    return age

def age_with_score():
    age_in_days = age().days
    age_with_score = (age_in_days, AGE_WEIGHT)
    return age_with_score
