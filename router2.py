#!/usr/bin/python

#@author: Dmitri Malaniouk

import threading
import pickle
import socket
import sys

UPstatus = False
routerID = 2

class GameOfThreads1 (threading.Thread):
    def __init__(self,tablesBro):
        threading.Thread.__init__(self)
        self.tables = tablesBro
    def run(self):
        recieve(self.tables)

class GameOfThreads2 (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        broadcast()

def printInitial(temp):
	print ("")
	print ("+-----------------------------+")
	print("+|    - Router 0 costs -     |+")
	print ("+-----------------------------+")
	print("+| Router | Cost | Interface |+")
	for i in temp:
		print ( "+|   ", i[0],"  |  ", i[1], " |    ", i[2], "    |+")
	print ("+-----------------------------+")
	print ("")

def printUpdate(temp):
	print ("")
	print ("+------------------------------+")
	print("+|   - UPDATED Link Costs -   |+")
	print ("+------------------------------+")
	print("+| Router |  Cost | Interface |+")
	for i in temp:
		print  ("+|    ", i[0],"  | ", i[1], "  |    ", i[2], "    |+")
	print ("+------------------------------+")
	print ("")

def calculon(temp):
	count = 1
	while(count!=0):
		count=0
		for i in range(len(temp)):
			for j in range(len(temp)):
				for k in range(len(temp)):
					if( temp[i][j] > (temp[i][k] + temp[k][j]) ):
						temp[i][j] = temp[i][k] + temp[k][j]
						count+=1
						UPstatus = True
					else:
						UPstatus = False

def broadcast():
	s = socket.socket()
	host = "#################" #ENTER IP HERE
	port = 1200
	myhost = socket.gethostbyname(socket.gethostname())
	
	s.connect( (host,port) )
	s.send(str(routerID).encode())
	s.send(pickle.dumps(costTable))

	print ("WAITING FOR RESPONSE")
	msg = s.recv(1024).decode()
	print (msg)
	msg = s.recv(1024)
	msg = pickle.loads(msg)

	acc=0
	for i in msg:
		thisTable[acc][1] = i
		acc+=1
		
	# if(not UPstatus):						#IF THERE WERE NO UPDATES, IT MEANS THE TABLE IS SETTLED AND WE CAN ALL GO HOME
		# break
	printUpdate(thisTable)

def recieve(temp):
	s = socket.socket()
	host = ''
	port = 1200

	try:
		s.bind((host, port))
	except (s.error , msg):
		print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()

	print ('NOW LISTENING FOR REQUESTS ON PORT 1200')
	s.listen(1)
	
	client, addr = s.accept()
	while True:
		placeholder = client.recv(4).decode()	#RECIEVE ROUTERID
		if(int(placeholder) == routerID):
			break
		msg = client.recv(1024)					#RECIEVE ENCODED ARRAY OF COSTS
		msg = pickle.loads(msg)					#UNLOAD ARRAY
		msg = [int(i) for i in msg]				#CONVERT EACH OBJECT TO INT
		temp[int(placeholder)] = msg			#STICK THAT BAD BOY INTO OUT tableSUPREME
		
		#LET THE ROUTER KNOW WE RECIEVED THEIR TABLES AND PERFORM CALCULATIONS
		msg1 = "TABLE RECIEVED / PERFORMING CALCULATIONS"
		client.send(msg1.encode())
		
		#MEANWHILE ON THIS ROUTER...
		print ("")
		print ("- RECIEVED Costs FROM ROUTER ", placeholder, " -")
		for i in msg:
			print ("/", i ,"/")
		print ("")
		
		print ("PERFORMING CALCULATIONS")
		calculon(temp)							#THIS WILL RETURN THE UPDATED TABLE
		
		msg = temp[int(placeholder)]			#RETRIEVE THE NEW COSTS FOR THE ROUTER WE RECIEVED
		client.send(pickle.dumps(msg))			#TOSS IT BACK TO THE BLOODY ROUTER
		if(not UPstatus):						#IF THERE WERE NO UPDATES, IT MEANS THE TABLE IS SETTLED AND WE CAN ALL GO HOME
			break
		
	client.close()
	print ("Server: Connection Closed")						
#router 0


print ("THIS IS ROUTER 2 BROADCASTING ON 128.235.208.35:1200")

#ROUTER 2 DETAILED COST TABLE
		#ROUTER | COST | INTERFERENCE
route0 = [0,        3,        	2]
route1 = [1,		1,		   	0]
route2 = [2,		0,		   	"~"]
route3 = [3,		2,			1]

thisTable = [route0, route1, route2, route3]

#ROUTER 2 COST TABLE
# [3, 1, 0, 2]
costTable = [route0[1], route1[1], route2[1], route3[1]]

#THIS TABLE WILL HOLD VALUES FOR ALL ROUTERS ON THE NETWORK
tableSUPREME = [[99, 99, 99, 99],[99, 99, 99, 99],costTable,[99, 99, 99, 99]]

#PRINT TABLE
printInitial(thisTable)


recieving = GameOfThreads1(tableSUPREME)	#recieve
shipping = GameOfThreads2()					#broadcast

try:
   recieving.start()
   shipping.start()
except:
   print ("CALL HOUSTON, CAUSE WE GOT AN ERROR")
