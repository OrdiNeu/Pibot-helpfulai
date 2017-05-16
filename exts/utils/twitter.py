# Twitter hook for pibot
import tweepy

API = None  # Initialized to tweepy.API in init()

def init(consumer_key, consumer_secret, access_token, access_token_secret):
    """Initialize the twitter API"""
    global API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    API = tweepy.API(auth)
