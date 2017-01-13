import time
from actionfactory.builder import *
import random
import pyamf
import zlib
import base64
class CityManager:
	def __init__(self,client):
		self.sender=client
		self.city=client.registernewplayer()['data']['player']['castles'][0]
		self.player=client.registernewplayer()['data']['player']['playerInfo']
		self.builder=Builder(client)
		self.availablequeue=self.isbuildqueueavailable()
		self.townhalllevel=self.gettownhalllevel()
		self.freeinteriorpositions=self.getfreeinteriorbuildingposition()
		self.barrackpositions=self.getbarrackpos()
		self.researches=self.getresearchlist()
		self.isresqueueavailable=self.isresqueueavailabl()
		self.resources=self.gettotalresource()
		self.freeexteriorpositions=self.getfreeexteriorpositions()
		self.troopqueued=self.getproducequeue()
		self.sender.client.sendmessage("common.setEventDone",{"id":1})
	def getproducequeue(self):
		self.sender.client.sendmessage("troop.getProduceQueue",{"castleId":self.city['id']})
		return self.sender.responsehandler('troop.getProduceQueue')['data']
	def getfreeexteriorpositions(self):
		outsidemin=1001
		outsidemax=1001+10+3*(self.gettownhalllevel())
		q=[u['positionId'] for u in self.city['buildings']]
		return [p for p in range(outsidemin,outsidemax) if p not in q]
	def isresqueueavailabl(self):
		t=0
		for p in self.researches:
			if p['upgradeing']:
				t+=1
		return (t==0)
	def getresearchlist(self):
		self.sender.client.sendmessage("tech.getResearchList",{"castleId":self.city['id']})
		res=self.sender.responsehandler("tech.getResearchList")
		q=[]
		for p in res['data']['acailableResearchBeans']:
			q.append(p)
		return q
	def getbarrackpos(self):
		q=[]
		for p in self.city['buildings']:
			if p['typeId']==2:
				q.append(p)
		return q
	def gettotalresource(self):
		x=self.city
		res=[x['resource']['food']['amount'],x['resource']['wood']['amount'],x['resource']['stone']['amount'],x['resource']['iron']['amount'],x['resource']['gold']]
		for fg in x['trades']:
			if fg['tradeType']==0:
				res[fg['resType']]+=fg['amount']
			else:
				res[-1]+=fg['amount']*fg['price']
		for gt in x['transingTrades']:
			res[gt['resType']]+=gt['amount']
		return res
	def getbarrackposforarcher(self):
		q=[]
		for p in self.city['buildings']:
			if (p['typeId']==2)&(p['level']>=4):
				q.append(p['positionId'])
		return q
	def trainarcher(self):
		q=self.getbarrackposforarcher()
		if q==[]:
			return
		self.sender.client.sendmessage("interior.modifyCommenceRate",{"castleId":self.city['id'],"foodrate":0,"woodrate":0,"stonerate":0,"ironrate":0})
		res=self.sender.responsehandler('interior.modifyCommenceRate')
		self.sender.client.sendmessage("troop.produceTroop",{"castleId":self.city['id'],"positionId":q[0],"troopType":7,"num":int(self.city['resource']['curPopulation']/2),"isShare":True,"toIdle":False})
		self.sender.client.sendmessage("interior.modifyCommenceRate",{"castleId":self.city['id'],"foodrate":100,"woodrate":0,"stonerate":0,"ironrate":0})
		res=self.sender.responsehandler('interior.modifyCommenceRate')
	def isbuildqueueavailable(self):
		curtime=time.time()*1000
		if (curtime-self.player['createrTime'])<72*3600000:
			total=2
		else:
			total=1
		t=0
		for p in self.city['buildings']:
			if p['status']!=0:
				t+=1
		return total-t
	def getfreeinteriorbuildingposition(self):
		occupied=[]
		for p in self.city['buildings']:
			occupied.append(p['positionId'])
		return [i for i in range(1,32) if i not in occupied]
	def buildrally(self):
		for p in self.city['buildings']:
			if p['typeId']==29:
				return
		if self.availablequeue>0:
			u=self.freeinteriorpositions[0]
			self.builder.createbuilding(self.city['id'],u,29)
			self.freeinteriorpositions=self.freeinteriorpositions[1:]
	def buildlevel1barrack(self):
		if self.availablequeue<=0:
			return
		self.buildrally()
		for p in self.freeinteriorpositions:
			self.builder.createbuilding(self.city['id'],p,2)
			self.barrackpositions.append({'positionId':p,'level':1,'status':1})
	def upgradebarrack(self,level):
		for p in self.barrackpositions:
			if self.availablequeue<=0:
				return
			if p['level']==level:
				if p['status']!=0:
					continue
				self.builder.upgradebuilding(self.city['id'],p['positionId'],2,level)
				self.availablequeue-=1
	def checkacademylevel(self):
		for p in self.city['buildings']:
			if p['typeId']==25:
				return p['level']
		return -1
	def getbuildingcount(self,t):
		total=[]
		for p in self.city['buildings']:
			if p['typeId']==t:
				total.append(p)
		return total
	def democottages(self):
		c=self.getbuildingcount(1)
		for r in c[2:]:
			if self.availablequeue<=0:
				return
			if r['status']!=0:
				continue
			self.builder.destructbuilding(self.city['id'],r['positionId'])
			r['status']=1
			self.availablequeue-=1
	def getresearchlevel(self,t):
		for p in self.researches:
			if p['typeId']==t:
				return p['avalevel']
		return 0
	def upgradecottages(self):
		c=self.getbuildingcount(1)
		if len(c)>2:
			return
		for p in c:
			if p['level']>=6:
				continue
			if p['status']!=0:
				continue
			if self.availablequeue<=0:
				return
			self.builder.upgradebuilding(self.city['id'],p['positionId'],1,p['level'])
			self.availablequeue-=1
	def getbuildinglevel(self,t):
		for p in self.city['buildings']:
			if p['typeId']==t:
				return p['level']
		return 0
	def upgradebuildingbytype(self,t):
		if self.availablequeue<=0:
			return
		x=-1
		for p in self.city['buildings']:
			if p['typeId']==t:
				x=p['positionId']
				y=p['level']
				if p['status']!=0:
					return
		if x==-1:
			return
		self.builder.upgradebuilding(self.city['id'],x,t,y)
		self.availablequeue-=1
	def research(self,t):
		if not self.isresqueueavailable:
			return
		x=self.getresearchlevel(t)
		if t==8:
			if self.getbuildinglevel(22)<x+1:
				self.upgradebuildingbytype(22)
				return
		if t==14:
			if self.getbuildinglevel(25)<4:
				self.upgradebuildingbytype(25)
				return
			if self.getresearchlevel(8)<4:
				self.research(8)
				return
		self.sender.client.sendmessage('tech.research',{'castleId':self.city['id'],'techId':t})
		self.isresqueueavailable=False
	def researcharchery(self):
		x=self.getresearchlevel(14)
		if x>=4:
			x=self.getresearchlevel(8)
			if x>=9:
				return
			self.research(8)
			return
		x=self.getresearchlevel(14)
		if x>=9:
			return
		self.research(14)
	def dotrades(self):
		p=self.resources[4]
		if p<5000000:
			self.sender.client.sendmessage("trade.newTrade",{"castleId":self.city['id'],"resType":0,"tradeType":1,"amount":2000000,"price":"1"})
			print "Selling food"
		for i in range(0,4):
			p=self.resources[i]
			if p<8000000:
				amount=int(20000000-p)
				if i==0:
					price=str(float(random.randint(10,100))/1000)
				else:
					price="0.001"
				self.sender.client.sendmessage("trade.newTrade",{"castleId":self.city['id'],"resType":i,"tradeType":0,"amount":amount,"price":price})
				resources=['food','wood','stone','iron']
				print ("Buying "+str(amount)+" "+resources[i]+" at price "+str(price))
	def demoall(self):
		for p in self.city['buildings']:
			if p['positionId']>1000:
				continue
			if p['typeId'] in [1,2,23,22,29]:
				continue
			if p['positionId'] in [-1,-2]:
				continue
			if self.availablequeue<=0:
				continue
			if p['status']!=0:
				continue
			self.builder.destructbuilding(self.city['id'],p['positionId'])
			self.availablequeue-=1
	def upgrademarket(self):
		q=self.getbuildinglevel(23)
		if q<5:
			self.upgradebuildingbytype(23)
	def gettownhalllevel(self):
		for p in self.city['buildings']:
			if p['positionId']==-1:
				return p['level']
	def demofields(self):
		for p in self.city['buildings']:
			if p['positionId']<1000:
				continue
			if p['status']!=0:
				continue
			if self.availablequeue<=0:
				return
			if p['typeId']!=7:
				self.builder.destructbuilding(self.city['id'],p['positionId'])
				self.availablequeue-=1
	def fastcreatefarm(self,pos,level):
		for i in range(level,4):
			if i==0:
				self.builder.createbuilding(self.city['id'],pos,7)
				continue
			self.builder.upgradebuilding(self.city['id'],pos,7,i)
	def createfarm(self):
		if self.availablequeue<=0:
			return
		for j in self.freeexteriorpositions:
			self.fastcreatefarm(j,0)
		for u in self.buildings:
			if (u['positionId']>1000)&(u['typeId']==7):
				if u['status']!=0:
					continue
				self.fastcreatefarm(u['positionId'],u['level'])
	def upgradefarm(self):
		for p in self.city['buildings']:
			if self.availablequeue<=0:
				return
			if (p['typeId']==7)&(p['level']<9)&(p['status']==0):
				self.builder.upgradebuilding(self.city['id'],p['positionId'],7,p['level'])
				self.availablequeue-=1
	def demoworstbuilding(self):
		demo=-1
		lev=10
		for p in self.city['buildings']:
			if p['typeId']==2:
				if p['level']<=lev:
					lev=p['level']
					demo=p['positionId']
		if demo!=-1:
			if self.availablequeue<=0:
				return
			self.builder.destructbuilding(self.city['id'],demo)
			self.availablequeue-=1
	def checkforge(self):
		for p in self.city['buildings']:
			if p['typeId']==22:
				return
		if self.freeexteriorpositions==[]:
			self.demoworstbuilding()
			return
		if self.availablequeue<=0:
			return
		q=self.freeexteriorpositions[0]
		self.freeexteriorpositions=self.freeexteriorpositions[1:]
		self.builder.createbuilding(self.city['id'],q,22)
		self.availablequeue-=1
	def dobuilding(self):
		self.upgrademarket()
		self.dotrades()
		self.researcharchery()
		self.democottages()
		self.demoall()
		self.upgradecottages()
		self.checkforge()
		self.buildlevel1barrack()
		for i in range(1,4):
			self.upgradebarrack(i)
		self.demofields()
		self.createfarm()
		self.upgradefarm()
		for i in range(4,9):
			self.upgradebarrack(i)
		if self.getresearchlevel(14)>=4:
			self.trainarcher()
	def getresourcesummary(self):
		f="f:"+str(int(self.city['resource']['food']['amount']))+",w:"+str(int(self.city['resource']['wood']['amount']))+",s:"+str(int(self.city['resource']['stone']['amount']))+",i:"+str(int(self.city['resource']['iron']['amount']))+",g:"+str(int(self.city['resource']['gold']))
		return f
	def gettroopsummary(self):
		troops={"peasants":'wo',"militia":'w',"scouter":'s',"pikemen":'p',"swordsmen":'sw',"archer":'a',"carriage":'t',"lightCavalry":'c',"heavyCavalry":'cata',"ballista":'b',"batteringRam":'r',"catapult":'cp'}
		yu=""
		for p in self.city['troop']:
			if self.city['troop'][p]<=0:
				continue
			if yu!="":
				yu+=','
			yu+=(troops[p]+":"+str(self.city['troop'][p]))
		return yu
	def debugstring(self):
		tr=self.sender.registernewplayer()['data']['player']
		tr['castles'][0]['troopqueued']=self.troopqueued
		tr['castles'][0]['researches']=self.researches
		trr=pyamf.encode(tr).read()
		trr=zlib.compress(trr)
		trr=base64.b64encode(trr)
		z={'accname':self.player['accountName'],'summary_resources':self.getresourcesummary(),'summary_troops':self.gettroopsummary(),'summary_attacks':0,'summary_username':self.player['userName'],'player':trr,'server':'Falx (na59)','warlog':''}
		return z