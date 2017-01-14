import urllib2
for i in range(0,2000):
  try:
    urllib2.urlopen('http://e2.eimg.us/EvonyClient'+str(i)+".swf")
    print ("Working "+str(i))
  except:
    print ("Not Working "+str(i))
