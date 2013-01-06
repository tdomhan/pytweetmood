import pickle
from urllib2 import urlopen
from urllib import urlencode
import urllib2
import base64
import urllib
import simplejson
import sys
import bingtrans

tweettranslations = {}
tweets = pickle.load(open('tweets.pickle'))

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
  

i=0
for tweet in tweets:
  try:
    print tweet.text
    t = translate('es','en',tweet.text.encode('utf-8'))
    print t
    print ""
    tweettranslations[tweet.id] = t
  except KeyboardInterrupt:
    break
  except Exception as e:
    print e
    tweettranslations.append("")
  i+=1
  print "%.2f" % (100.*i/len(tweets))


pickle.dump(tweettranslations, open('tweets-en.pickle', 'w'))
