import sys, os

try:
	inp = open(sys.argv[1], 'rb')
	out = open(sys.argv[2], 'w+b')
except:
	print 'Please check the input args'

pos = 0

while pos < os.path.getsize(sys.argv[1]):
	b = inp.read(8)
	for i in reversed(range(8)):
		out.write(b[i])
	pos += 8
	
inp.close()
out.close() 
