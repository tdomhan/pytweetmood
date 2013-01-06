import sys
from textwrap import TextWrapper
import tweepy
import pickle
import re
import urllib2
import urllib
import time
import tweet_features
import random
from time import gmtime, strftime

access_token  = pickle.load(open('twitter_access_token.pickle','r'))

classifier = pickle.load(open('classifier.pickle', 'r'))
worstfeaturesfilter = pickle.load(open('worstfeaturesfilter.pickle', 'r'))

jokes = pickle.load(open('jokes.pickle'))
random.shuffle(jokes)

#application secrets!
consumer_key = "hCBUNdliK9Ta3Y1rBKeY9w"
consumer_secret = "sJekHwDIl17JuwcukNalcs7mynSJABbieZg8Y07AzY"

#account credential
username = 'spass_muss_sein'
password = 'chiste'

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
#access token was created like this: http://packages.python.org/tweepy/html/auth_tutorial.html
auth.set_access_token(access_token.key, access_token.secret)
api = tweepy.API(auth_handler=auth, secure=True, retry_count=3)

def tweet_split(l):
        n=140
        for i in xrange(0, len(l), n):
        	yield l[i:i+n]

class StreamListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')
    def on_error(self, code):
        print code
        return False
    def on_status(self, status):
        try:
            if not status.retweeted and not status.in_reply_to_status_id and not status.in_reply_to_user_id and not hasattr(status, 'retweeted_status'):
                features = tweet_features.get_tweet_features(status.text, worstfeaturesfilter)
		print features
	    	mood = classifier.classify(features)
                if mood == 'negative':
                	if len(jokes) > 0:
				#TODO: respect word boundaries
                		jokechunks = jokes.pop()
				pickle.dump(jokes,open('jokes.pickle', 'w'))

   				for chunk in jokechunks:
					api.update_status(chunk)	
     			else:
				print "we're out of jokes!!"		
                print self.status_wrapper.fill(status.text)
                print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
		print "mood classified as: %s" % mood
		classifier.explain(features)
        except Exception, e:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            print e
            pass



print 'opening stream'

l = StreamListener()
streamer = tweepy.Stream(auth=auth, listener=l, timeout=300000)
u = api.get_user('murmurawhispers')
streamer.filter(follow = [u.id])


