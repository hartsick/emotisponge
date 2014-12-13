import random
from common import EVENT_NAMES, EVENT_VALUES
from age import age_with_score

HELP_TEXT = "i love new friends!! fave for fave? or maybe ask me how I'm doing? rly I just love attention! (:"

def generate_random_greeting():
  messages = [
    "hi hi hi hi hi",
    "hi how is it going?",
    "i saw the cutest doggy today",
    "agjlabbbbbb llpbbbbbb llpbb <3",
    "^.^",
    "little dogs have the cutest ears",
    "my butt is weird",
    "tableflip emoticon",
    "lets all listen to moondog ok?",
    "i like midnight dances",
    "lemons lemons lemons lemons"
  ]
  return random.choice(messages)


def generate_emo_status(redis, wordApi):
  score = get_emo_score(redis)

  if score >= 75:
    seed_word = "elated"
    mood = get_synonym(wordApi, seed_word)
    return "I'm feeling "+mood+"! :D :D :D :D :D   ({0})".format(score)

  elif score >= 50:
    seed_word = "happy"
    mood = get_synonym(wordApi, seed_word)
    return "ohhh im p "+mood+", u know? (:   ({0})".format(score)

  elif score >= 25:
    seed_word="okay"
    mood = get_synonym(wordApi, seed_word)
    return "i dunno, feelin' pretty "+mood+" rite now but maybe its just a bad day :|   ({0})".format(score)

  elif score > 10:
    seed_word="lonely"
    mood = get_synonym(wordApi, seed_word)
    return "i could really really use a friend right now. feelin' rly "+mood+". :(   ({0})".format(score)

  elif score <= 10:
    seed_word="depressed"
    mood = get_synonym(wordApi, seed_word)
    return "D; I am so "+mood+"...   ({0})".format(score)


def get_synonym(wordApi, word):
  wordnik_synonyms = wordApi.getRelatedWords(word, relationshipTypes='synonym')

  synonyms = wordnik_synonyms[0].words

  return random.choice(synonyms)


def get_emo_score(redis):
  event_counts = redis.mget(*EVENT_NAMES)

  score = 0
  index = 0

  # add 'em up
  for event, value in EVENT_VALUES.iteritems():
    score += (value * int(event_counts[index]))
    index += 1

  # adjust by length of time bot has been around
  score = score - calculate_age_score(redis)

  return score


def calculate_age_score(redis):
  scored_age = age_with_score(redis)
  score = scored_age[0] * scored_age[1]

  return score
