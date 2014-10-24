from datetime import datetime
import time
import logging
import json
import edgesense.utils as eu

""" Maps the tweet data in a conventional format.
    If a tweets is invalid then it is mapped to None
"""
def map_data(tweet):
    try:
        mapped = {}
        mapped['id_str'] = tweet['id_str']
        mapped['screen_name'] = tweet['from_user']
        mapped['user_id'] = tweet['from_user_id_str']
        created = datetime.strptime(tweet['time'], '%d/%m/%Y %H:%M:%S')
        mapped['created_ts'] = int(time.mktime(created.timetuple()))
        entities = json.loads(tweet['entities_str'])
        mapped['user_mentions'] = [{'screen_name': t['screen_name'], 'user_id': t['id_str']} for t in entities['user_mentions']]
        mapped['text'] = tweet['text']
        return mapped
    except:
        return None

""" Loads the CSV and parses the tweets contained
    We expect one tweet per row, and allow sorting 
    the tweets if needed.
    The empty tweets are rejected.
"""
def load_and_parse(source, sort_key=None, dump_to=None):
    raw_tweets = eu.resource.load_csv(source, dump_to=dump_to)
    tweets = [map_data(t) for t in raw_tweets]
    tweets = [t for t in tweets if t]
    logging.info("Parsing tweets - read %(t)i tweets in CSV, using %(v)i valid tweets" % {'t': len(raw_tweets), 'v': len(tweets)})
    return sorted(tweets, key=eu.sort_by(sort_key))
