import pickle
from urllib2 import urlopen
from urllib import urlencode
import urllib2
import base64
import urllib
import simplejson
import sys
import bingtrans

tweettranslations = []
tweets = pickle.load(open('tweets.pickle'))
tweetsen = pickle.load(open('tweets-en.pickle'))
tweetlabel = pickle.load(open('tweetlabel.pickle'))


def translate(fr, to, text):
  baseurl = "https://api.datamarket.azure.com/Bing/MicrosoftTranslator/v1/Translate?"
  fromparam = 'From'
  textparam = 'Text'
  toparam = 'To'
  to = "'" + to + "'"
  fr = "'" + fr + "'"
  text = "'" + text + "'"
  paramstr = urllib.urlencode({fromparam:fr, textparam:text, toparam:to, '$format': 'json'})
  url = baseurl + paramstr

  username = ''
  password = 'uUs4CSSRsCr1phyfoarRWSUrpraBZ6Ip2xM9ODBi54I='

  request = urllib2.Request(url)
  base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  result = result.readlines()[0]

  json = simplejson.loads(result)
  return json['d']['results'][0]['Text']

inputmapping = {'1': 'positive', '2': 'negative', '3': 'neutral', '4': 'irrelevant'}

input = ''

try:
  i=0
  for tweet in tweets:
    print tweet.text
    if not tweet.id in tweetlabel:
      if tweet.id in tweetsen:
        print tweetsen[tweet.id]
      else:
        print translate('es','en',tweet.text.encode('utf-8'))

      while not input in inputmapping: 
        input = raw_input('Enter your label(pos(1)/neg(2)/neu(3)/irr(4)/):')
      tweetlabel[tweet.id] = inputmapping[input]

    input = ''
    i += 1
    print "%.2f" % (100.*i/len(tweets))
except KeyboardInterrupt:
  pass

pickle.dump(tweetlabel, open('tweetlabel.pickle', 'w'))

