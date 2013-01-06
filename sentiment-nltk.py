# coding=utf8
"""
@package sentiment
Twitter sentiment analysis.

This code performs sentiment analysis on Tweets.

"""
import csv, random
import tweet_features
import pickle
import nltk
import nltk.metrics
from nltk.classify.svm import SvmClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from collections import defaultdict

random.seed(10)

# read all tweets and labels
tweetsorig = pickle.load(open('tweets.pickle'))
tweetsen = pickle.load(open('tweets-en.pickle'))
tweetlabel = pickle.load(open('tweetlabel.pickle'))

tweets = []
labelcount = defaultdict(int)
for tweet in tweetsorig:
  if tweet.id in tweetlabel:
    label = tweetlabel[tweet.id]
    if label == 'positive':
      tweets.append( (tweet.text,label) );
    elif label == 'negative':
      tweets.append( (tweet.text,label) );
    labelcount[label] += 1

random.shuffle(tweets)
print labelcount


# split in to training and test sets
random.shuffle( tweets );

num_train = int(0.8 * len(tweets))

#fvecs = [(tweet_features.make_tweet_dict(t),s) for (t,s) in tweets]
fvecs = [(tweet_features.get_tweet_features(t, set()),s) for (t,s) in tweets]
v_train = fvecs[0:num_train]
#v_train = fvecs
v_test  = fvecs[num_train:len(tweets)]


#extract best word features
word_fd = FreqDist()
label_word_fd = ConditionalFreqDist()

for (feats, label) in fvecs:
  for key in feats:
    if feats[key]:
      word_fd.inc(key)
      label_word_fd[label].inc(key)

pos_word_count = label_word_fd['positive'].N()
print pos_word_count
neg_word_count = label_word_fd['negative'].N()
print neg_word_count
total_word_count = pos_word_count + neg_word_count

feature_scores = {}

for feature, freq in word_fd.iteritems():
  pos_score = BigramAssocMeasures.chi_sq(label_word_fd['positive'][feature],
                                         (freq, pos_word_count), total_word_count)
  neg_score = BigramAssocMeasures.chi_sq(label_word_fd['negative'][feature],
                                         (freq, neg_word_count), total_word_count)
  feature_scores[feature] = pos_score + neg_score

sorted_feature_scores = sorted(feature_scores.iteritems(), key=lambda (w,s): s, reverse=True)
sorted_features = [w for (w,s) in sorted_feature_scores]
print "best features:"
for w in sorted_features[0:100]:
  print w

print len(sorted_features)
#exit()

worst = sorted_feature_scores[14000:]#4000
worstfeaturesfilter = set([w for w, s in worst])

#filter the feature vectors:
fvecs = [(tweet_features.get_tweet_features(t, worstfeaturesfilter),s) for (t,s) in tweets]
v_train = fvecs[0:num_train]
#v_train = fvecs
v_test  = fvecs[num_train:len(tweets)]

# dump tweets which our feature selector found nothing
#for i in range(0,len(tweets)):
#    if tweet_features.is_zero_dict( fvecs[i][0] ):
#        print tweets[i][1] + ': ' + tweets[i][0]


# train classifier
#classifier = nltk.NaiveBayesClassifier.train(v_train);
#classifier = nltk.classify.maxent.train_maxent_classifier_with_gis(v_train);
classifier = SvmClassifier.train(v_train)
#classifier = nltk.classify.maxent.train_maxent_classifier_with_gis(v_train,count_cutoff=2)
#classifier = nltk.classify.maxent.train_maxent_classifier_with_iis(v_train,count_cutoff=4)
#classifier = nltk.classify.maxent.train_maxent_classifier_with_scipy(v_train, algorithm='BFGS');

pickle.dump(worstfeaturesfilter, open('worstfeaturesfilter.pickle', 'w'))
print "WARNING: NOT PICKELING CLASSIFIER ANYMORE"
#pickle.dump(classifier, open('classifier.pickle', 'w'))

#print classifier.classify(tweet_features.get_tweet_features("Christmas Eve without my, with cold feet and nobody to.", worstfeaturesfilter))
#print classifier.classify(tweet_features.get_tweet_features("Nochebuena sin mi @ tdomhan, con los pies fríos y nadie a quien abrazar.", worstfeaturesfilter))
#print classifier.classify(tweet_features.get_tweet_features("Nochebuena sin mi, con los pies fríos y nadie a quien abrazar.", worstfeaturesfilter))
#print classifier.explain(tweet_features.get_tweet_features("Nochebuena sin mi @ tdomhan, con los pies fríos y nadie a quien abrazar.", worstfeaturesfilter))


# classify and dump results for interpretation

refsets = defaultdict(set)
testsets = defaultdict(set)

for i, (feats, label) in enumerate(v_test):
  refsets[label].add(i)
  observed = classifier.classify(feats)
  testsets[observed].add(i)

#classifier.show_most_informative_features(n=500)

print 'accuracy %f' % nltk.classify.accuracy(classifier, v_test)
print 'pos precision:', nltk.metrics.precision(refsets['positive'], testsets['positive'])
print 'pos recall:', nltk.metrics.recall(refsets['positive'], testsets['positive'])
print 'pos F-measure:', nltk.metrics.f_measure(refsets['positive'], testsets['positive'])
print 'neg precision:', nltk.metrics.precision(refsets['negative'], testsets['negative'])
print 'neg recall:', nltk.metrics.recall(refsets['negative'], testsets['negative'])
print 'neg F-measure:', nltk.metrics.f_measure(refsets['negative'], testsets['negative'])

print 'Confusion Matrix'
test_truth   = [s for (t,s) in v_test]
test_predict = [classifier.classify(t) for (t,s) in v_test]
print nltk.ConfusionMatrix( test_truth, test_predict )

exit()

i=0
for (t,s) in v_test:
  predlabel = classifier.classify(t)
  if s != predlabel:
    print "classified as %s but is %s" % (predlabel, s)
    (text, label) = tweets[num_train+i]
    print text
    print t
    print classifier.explain(t)
    print ""
  i+=1

exit()

# build confusion matrix over test set
test_truth   = [s for (t,s) in v_test]
test_predict = [classifier.classify(t) for (t,s) in v_test]

for i in range(0, len(test_truth)):
  if test_truth[i] != test_predict[i]:
    print tweets[i]

print '\nAccuracy %f\n' % nltk.classify.accuracy(classifier, v_test)

print 'Confusion Matrix'
print nltk.ConfusionMatrix( test_truth, test_predict )

#classifier.most_informative_features()
classifier.show_most_informative_features(n=100)

fids = sorted(range(len(classifier._weights)), key=lambda fid: abs(classifier._weights[fid]), reverse=True)
#for fid in fids:
# print '%8.3f %s' % (classifier._weights[fid],classifier._encoding.describe(fid))

print len(fids)

print classifier.classify(tweet_features.get_tweet_features(u"Oye @alascurain, happy belated birthday! Bienvenido al club de los 25!!! Seguro la pasaste y la seguirás pasando muy bien! Muchos besos :)"))

print classifier.classify(tweet_features.get_tweet_features(u"Casual que tú vas a sentarte afuera del museo y tu alemán aparece en el folleto del museo por desarrollar un app para una exposición."))

print classifier.classify(tweet_features.get_tweet_features(u"A los burócratas deberíamos llamarlos sirvientes civiles. Para que no se les suban los humos."))
