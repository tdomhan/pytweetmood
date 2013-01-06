"""
@package tweet_features
Convert tweet to feature vector.

These routines help convert arbitrary tweets in to feature vectors.

"""
from nltk import bigrams, trigrams
import re
from nltk.tokenize import wordpunct_tokenize
import HTMLParser
import string
h = HTMLParser.HTMLParser()

#parse spanish sentiment dictionary
#sentdictdata = open('spanishsentimentdictionary/mediumStrengthLexicon.txt').readlines()
#sentdict = {}
  #for s in sentdictdata:
  #d = s.split()
  #sentdict[d[0]] = d[2]

#print sentdict


# search patterns for features
testFeatures = \
    [('hasAddict',     (' addict',)), \
     ('hasAwesome',    ('awesome',)), \
     ('hasBroken',     ('broke',)), \
     ('hasBad',        (' bad',)), \
     ('hasBug',        (' bug',)), \
     ('hasCant',       ('cant','can\'t')), \
     ('hasCrash',      ('crash',)), \
     ('hasCool',       ('cool',)), \
     ('hasDifficult',  ('difficult',)), \
     ('hasDisaster',   ('disaster',)), \
     ('hasDown',       (' down',)), \
     ('hasDont',       ('dont','don\'t','do not','does not','doesn\'t')), \
     ('hasEasy',       (' easy',)), \
     ('hasExclaim',    ('!',)), \
     ('hasExcite',     (' excite',)), \
     ('hasExpense',    ('expense','expensive')), \
     ('hasFail',       (' fail',)), \
     ('hasFast',       (' fast',)), \
     ('hasFix',        (' fix',)), \
     ('hasFree',       (' free',)), \
     ('hasFrowny',     (':(', '):')), \
     ('hasFuck',       ('fuck',)), \
     ('hasGood',       ('good','great')), \
     ('hasHappy',      (' happy',' happi')), \
     ('hasHate',       ('hate',)), \
     ('hasHeart',      ('heart', '<3')), \
     ('hasIssue',      (' issue',)), \
     ('hasIncredible', ('incredible',)), \
     ('hasInterest',   ('interest',)), \
     ('hasLike',       (' like',)), \
     ('hasLol',        (' lol',)), \
     ('hasLove',       ('love','loving')), \
     ('hasLose',       (' lose',)), \
     ('hasNeat',       ('neat',)), \
     ('hasNever',      (' never',)), \
     ('hasNice',       (' nice',)), \
     ('hasPoor',       ('poor',)), \
     ('hasPerfect',    ('perfect',)), \
     ('hasPlease',     ('please',)), \
     ('hasSerious',    ('serious',)), \
     ('hasShit',       ('shit',)), \
     ('hasSlow',       (' slow',)), \
     ('hasSmiley',     (':)', ':D', '(:')), \
     ('hasSuck',       ('suck',)), \
     ('hasTerrible',   ('terrible',)), \
     ('hasThanks',     ('thank',)), \
     ('hasTrouble',    ('trouble',)), \
     ('hasUnhappy',    ('unhapp',)), \
     ('hasWin',        (' win ','winner','winning')), \
     ('hasWinky',      (';)',)), \
     ('hasWow',        ('wow','omg')) ]


def make_tweet_nparr( txt ):
    """ 
    Extract tweet feature vector as NumPy array. 
    """
    # result storage
    fvec = numpy.empty( len(testFeatures) )

    # search for each feature
    txtLow = ' ' + txt.lower() + ' '
    for i in range( 0, len(testFeatures) ):

        key = testFeatures[i][0]

        fvec[i] = False
        for tstr in testFeatures[i][1]:
            fvec[i] = fvec[i] or (txtLow.find(tstr) != -1)

    return fvec

def get_tweet_features(txt, filter):
  all = []
  pat = r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^%s\s]|/)))'
  pat = pat % re.escape(string.punctuation)
  txt = re.sub(pat, ' URL ', txt)
  txt = h.unescape(txt)
  #txt = re.sub('<3', ' heart ', txt)
  words = wordpunct_tokenize(txt)
  #print txt
  #print [w.lower() for w in words]
  #print ""
  
  #verniedlichungsfeature!
  
  unigram = get_word_features(words)
  all.extend(unigram)
  
  wordshape = get_word_shape_features(words)
  all.extend(wordshape)
  
  markfeatures = get_mark_features(txt, words)
  all.extend(markfeatures)
  
  specialwordfeatures = get_special_word_features(txt, words)
  all.extend(specialwordfeatures)
  
  #sentdictfeatures = get_sent_dict_features(words)
  #all.extend(sentdictfeatures)

  bigramwordfeatures = get_wordbigrams_features(words)
  all.extend(bigramwordfeatures)
  
  trigramwordfeatures = get_wordtrigrams_features(words)
  all.extend(trigramwordfeatures)
  
  emoticonfeatures = get_emoticon_features(txt)
  all.extend(emoticonfeatures)
  
  #url domain extractor
  #http://t.co/x6BI96Ib -> URLt.co
  
  return dict([(f,w) for (f,w) in all if not f in filter])

def get_sent_dict_features(words):
  d = []
  num_pos = 0
  num_neg = 0
  for word in words:
    if word in sentdict:
      label = sentdict[word]
      if label == 'pos':
        num_pos += 1
      elif label == 'neg':
        num_neg += 1

  if num_pos < num_neg:
    d.append(("DICTMORENEG", True))

  if num_pos > num_neg:
    d.append(("DICTMOREPOS", True))

  if num_pos > 0:
    d.append(("DICTMPOSWORDS", True))

  if num_neg > 0:
    d.append(("DICTNEGWORDS", True))

  return d

def get_word_shape_features(words):
  d = []
  upp = False
  for word in words:
    if word.isupper() and len(word)>1:
      upp = True

  if upp:
    d.append(("UPPER", upp))
  return d

def get_mark_features(text, words):
  d = []
  #!!!!
  #?!?
  if re.search("!!+", text):
    d.append(("EXPLANATION", True))
  #  else:
  #d.append(("EXPLANATION", False))

  if re.search("\.\.+", text):
    d.append(("DOTS", True))
#  else:
#    d.append(("DOTS", False))

  result = re.search("[?!]+", text)
  if result and ('?' in result.group(0) and '!' in result.group(0)):
    d.append(("EXPLAQUESTION", True))
#else:
#   d.append(("EXPLAQUESTION", False))

  return d

def get_special_word_features(text, words):
  #TODO: iterate over words instead of using text
  
  #nooooooooooooooooooooooooo
  #hahahahah
  d = []
  if re.search("[HAah][HAah][HAah]+", text) or re.search("ja[ja]+", text):
    d.append(("HAHA", True))
  #else:
  # d.append(("HAHA", False))

  return d

def get_emoticon_features(text):
  #:D     (not split up)
  #:)     (not split up)
  #:'(    (not split up)
  #&lt;3  (split up by tokenizer)
  d = []
  if re.search("<3", text):
    d.append(("HEART", True))
  if re.search("\:\s?D", text):
    d.append(("BIGSMILE", True))
  
  #else:
  #  d.append(("HEART", False))
  return d

def get_wordbigrams_features(words):
  bigr = bigrams([w.lower() for w in words])
  #print bigr
  d = [(" ".join(b), True) for b in bigr]
  d = [(x,l) for (x,l) in d if not [p for p in string.punctuation if p in x]]
       #('#' in x or '@' in x or '\'' in x or '.' in x or ',' in x or '?' in x or '!' in x)]
  return d

def get_wordtrigrams_features(words):
  trigr = trigrams([w.lower() for w in words])
  d = [(" ".join(b), True) for b in trigr]
  d = [(x,l) for (x,l) in d if not [p for p in string.punctuation if p in x]]
  #print d
  return d

def get_word_features(words):
  
  d =  [(word.lower(), True) for word in words if len(word) > 1]
    #for i in range(0,100):
  #d.append(("blubb"+str(i), False))
  return d

def make_tweet_dict( txt ):
    """ 
    Extract tweet feature vector as dictionary. 
    """
    txtLow = ' ' + txt.lower() + ' '

    # result storage
    fvec = {}

    # search for each feature
    for test in testFeatures:

        key = test[0]

        fvec[key] = False;
        for tstr in test[1]:
            fvec[key] = fvec[key] or (txtLow.find(tstr) != -1)

    return fvec


def tweet_dict_to_nparr( dict ):
    """
    Convert dictionary feature vector to numpy array
    """
    fvec = numpy.empty( len(testFeatures) )

    for i in range( 0, len(testFeatures) ):
        fvec[i] = dict[ testFeatures[i][0] ]

    return fvec


def tweet_nparr_to_dict( nparr, use_standard_features=False ):
    """
    Convert NumPy array to dictionary
    """
    fvec = {}

    if use_standard_features:
        assert len(nparr) == len(testFeatures)
        fvec = {}
        for i in range( 0, len(nparr) ):
            fvec[ testFeatures[i][0] ] = nparr[i]

    else:
        for i in range( 0, len(nparr) ):
            fvec[ str(i) ] = nparr[i]

    return fvec


def is_zero_dict( dict ):
    """
    Identifies empty feature vectors
    """
    has_any_features = False
    for key in dict:
        has_any_features = has_any_features or dict[key]

    return not has_any_features
