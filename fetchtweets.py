import tweepy
import pickle

tweets = []
page = 1
while True:
  statuses = tweepy.api.user_timeline('murmurawhispers', count=100, page=page)
  if statuses:
    tweets.extend(statuses)
  else:
     # All done
    break
  page += 1  # next page

pickle.dump(tweets, open('tweets.pickle','w'))
