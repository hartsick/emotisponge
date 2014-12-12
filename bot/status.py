import random
from common import wordApi, redis, EVENT_NAMES, EVENT_VALUES
from age import age_with_score

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
    seed_word="okay"
    mood = get_synonym(seed_word)
    return "i dunno, feelin' pretty "+mood+" rite now but maybe its just a bad day :|"

  elif score > 10:
    seed_word="lonely"
    mood = get_synonym(seed_word)
    return "i could really really use a friend right now. feelin' rly "+mood+". :("

  elif score <= 10:
    seed_word="depressed"
    mood = get_synonym(seed_word)
    return "D; I am so "+mood+"..."


def get_synonym(word):
  wordnik_synonyms = wordApi.getRelatedWords(word, relationshipTypes='synonym')

  synonyms = wordnik_synonyms[0].words

  return random.choice(synonyms)


def get_emo_score():
  event_counts = redis.mget(*EVENT_NAMES)

  score = 0
  index = 0

  # add 'em up
  for event, value in EVENT_VALUES.iteritems():
    score += (value * int(event_counts[index]))
    index += 1

  print score

  # adjust by length of time bot has been around
  score = score - calculate_age_score()

  print score

  return score

def calculate_age_score():
  scored_age = age_with_score()
  score = scored_age[0] * scored_age[1]

  return score

print generate_emo_status()
