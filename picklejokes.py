import pickle

jokelines = open('jokes.txt').readlines()

jokes = []


for line in jokelines:
	line = line.strip()
	if line == "":
		continue

	line = '@murmurawhispers ' + line

	chunks = line.split('|')
	#make sure each chunk fits in a tweet
	for chunk in chunks:
		if len(chunk) > 140:
			print "joke too long:"
			print line	
			continue

	chunks.reverse()
	jokes.append(chunks)
	
#pickle the jokes
#print jokes
print len(jokes)
pickle.dump(jokes, open('jokes.pickle', 'w'))
