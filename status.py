from common import wordApi, redis, REDIS_KEYS
from wordnik import *
import random

def generate_random_greeting():
  # TODO: fill with messages
  messages = [
    "hi hi hi hi hi"
  ]
  return random.choice(messages)


def generate_emo_status():
  score = get_emo_score()

  if score >= 75:
    seed_word = "elated"
    mood = get_synonym(seed_word)
    return "I'm feeling "+mood+"! :D :D :D :D :D"

  elif score >= 50:
    seed_word = "happy"
    mood = get_synonym(seed_word)
    return "ohhh im p "+mood+", u know? (:"

  elif score >= 25:
    seed_word="content"
    mood = get_synonym(seed_word)
    return "i dunno, feelin' pretty"+mood+" rite now but maybe its just a bad day :|"

  elif score > 10:
    seed_word="lonely"
    mood = get_synonym(seed_word)
    return "i could really really use a friend right now. feelin' rly"+mood+". :("

  elif score <= 10:
    seed_word="depressed"
    mood = get_synonym(seed_word)
    return "D; I am so "+mood+"..."


def get_synonym(word):
  synonyms = wordApi.getRelatedWords(word=word, relationship_type='synonym')

  return random.choice(synonyms)


def get_emo_score():
  values = redis.mget(*REDIS_KEYS)
  print values
  return 20
