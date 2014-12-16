import json
import time
from datetime import datetime
import dateutil.parser as parser
from common import AGE_WEIGHT

def set_birth_time(twitter, redis):
    current_time = datetime.now()

    # Redis stores strings, so convert accordingly
    time_as_string = current_time.isoformat()
    redis.set('birth_date', time_as_string)

    human_readable_time = datetime.strftime(current_time,'%a, %B %d, %Y at %X %Z')

    twitter.update_status(status="An emotisponge was born at " + human_readable_time + "!")
    time.sleep(60)
    twitter.update_status(status="hellooooo, world! (: :)")
    time.sleep(60)
    twitter.update_status(status="luv me")


def get_birth_time(redis):
    string = redis.get('birth_date')
    date = parser.parse(string)

    return date


def age(redis):
    age = datetime.now() - get_birth_time(redis)

    return age


def age_with_score(redis):
    # age_in_days = age(redis).days
    age_in_hours = age(redis).hour

    age_with_score = (age_in_hours, AGE_WEIGHT)

    return age_with_score
