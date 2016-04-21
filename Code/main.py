import tweetment
import datetime

classifier = tweet.SentimentClassifier()#'./model.pkl')
	
for i in range(17):
	fname = './train/train'
	f = open('./out/train'+str(i), 'w')
	
	for line in open(fname + str(i)):
	  tweet = line.strip()
	  sentiment = classifier.classify(tweet)
	  #print sentiment
	  f.write(sentiment+ '\t' +tweet+'\n' )
	
	f.close()
