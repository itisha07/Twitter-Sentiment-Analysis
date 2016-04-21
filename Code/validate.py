from sklearn.metrics import confusion_matrix, classification_report
y_true= []
y_pred = []
o = open( './trained', 'r')
count = 0
for i in range(17):
	f = open("./out/train"+str(i))
	for line in f.readlines():
		l = o.readline()
		l = l.split('\t')
		line = line.split('\t')
		y_true.append(l[0])
		y_pred.append(line[0])
	f.close()
	count += 500
	
	if count % 1000 == 0 :
		print "Cross Validation fold -", count/1000
		
		print "Confusion Matrix "
		print confusion_matrix(y_true, y_pred, labels =["positive", "neutral", "negative"])
		print "Classification Report"
		print(classification_report(y_true, y_pred, target_names=["positive", "neutral", "negative"]))
		y_true= []
		y_pred = []
print confusion_matrix(y_true, y_pred, labels =["positive", "neutral", "negative"])
print(classification_report(y_true, y_pred, target_names=["positive", "neutral", "negative"]))
		
