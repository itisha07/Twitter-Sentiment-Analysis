
k = open( 'raw','r')
count = 0
f = open('./train'+str(int(count/500)), 'w')
for line in k.readlines():
	f.write(line)
	count += 1
	if( count % 500 == 0 ):
		f.close();
		f = open('./train'+str(int(count/500)), 'w')
	
f.close()