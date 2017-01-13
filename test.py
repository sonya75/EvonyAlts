from evony import *
from citymanager import *
import hashlib
from threading import Thread
import time
import random
import sys
import os
import json
def getemails(x):
	a=open(x,'r').read().split('\n')
	b=[]
	for p in a:
		q=p.split(' ')
		for u in q:
			if '@' in u:
				b.append(u.strip())
	return b
def makeround(x):
	if not os.path.exists('playerfiles'):
		os.mkdir('playerfiles')
	def uv(w):
		return
	while True:
		try:
			y=Client('na59',setproxy=True,proxyhost="127.0.0.1",proxyport=9050,proxytype="SOCKS5",timeout=30,callback=uv)
			break
		except:
			time.sleep(5)
	random.shuffle(x)
	for p in x:
		y.registered=False
		tyt=0
		try:
			y.client.sendmessage('login',{'user':p,'pwd':hashlib.sha1('aaaaaa').hexdigest()})
			y.loginresponsehandler()
		except:
			y.close()
			time.sleep(5)
			for tyt in range(0,20):
				try:
					y=Client('na59',setproxy=True,proxyhost="127.0.0.1",proxyport=9050,proxytype="SOCKS5",timeout=30,callback=uv)
					y.client.sendmessage('login',{'user':p,'pwd':hashlib.sha1('aaaaaa').hexdigest()})
					y.loginresponsehandler()
					break
				except:
					time.sleep(5)
		if tyt==19:
			continue
		try:
			fr=y.registernewplayer()
			fg=open(os.path.join('playerfiles',p.split('@')[0]+".evo"),'w')
			json.dump(fr['data'],fg)
			fg.close()
			c=CityManager(y)
			c.dobuilding()
		except:
			pass
		time.sleep(15)
	y.close()
	makeround(x)
d=getemails('mainalts.txt')
y=int(sys.argv[1])
q=0
while q<len(d):
	Thread(target=makeround,args=(d[q:(y+q)],)).start()
	time.sleep(15)
	q+=y