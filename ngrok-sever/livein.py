# Importing the json module.
import json
# Importing the socket module.
import socket
# Importing the sys module.
import sys
# Importing the threading module.
import threading
import pickle
import os
# import sys
import time
import requests

# Creating a global variable.

groups = {}
fileTransferCondition = threading.Condition()

# It's a class that represents a group of people
class Group:
	def __init__(self,admin,client):
		"""
		It initializes the class with the admin and client
		
		:param admin: The admin of the group
		:param client: the client object
		"""
		self.admin = admin
		self.clients = {}
		self.offlineMessages = {}
		self.allMembers = set()
		self.onlineMembers = set()
		self.joinRequests = set()
		self.waitClients = {}

		self.clients[admin] = client
		self.allMembers.add(admin)
		self.onlineMembers.add(admin)

	def disconnect(self,username):
		"""
		It removes the username from the list of online members and deletes the client from the dictionary
		of clients
		
		:param username: The username of the user who is connecting
		"""
		self.onlineMembers.remove(username)
		del self.clients[username]
	
	def connect(self,username,client):
		"""
		It adds the username to the set of online members and then adds the username and client to the
		dictionary of clients
		
		:param username: The username of the user who is connecting
		:param client: the client object that is connected to the server
		"""
		self.onlineMembers.add(username)
		self.clients[username] = client

	def sendMessage(self,message,username):
		"""
		It sends a message to all online members except the sender.
		
		:param message: The message that the user sent
		:param username: The username of the client that is sending the message
		"""
		for member in self.onlineMembers:
			if member != username:
				self.clients[member].send(bytes(username + ": " + message,"utf-8"))

def pyconChat(client, username, groupname):
	"""
	It's a function that handles all the commands that the client can send to the server.
	
	:param client: The client socket
	:param username: The username of the client
	:param groupname: The name of the group the user is in
	"""
	while True:
		msg = client.recv(1024).decode("utf-8")
		if msg == "/viewRequests":
			client.send(b"/viewRequests")
			client.recv(1024).decode("utf-8")
			if username == groups[groupname].admin:
				client.send(b"/sendingData")
				client.recv(1024)
				client.send(pickle.dumps(groups[groupname].joinRequests))
			else:
				client.send(b"You're not an admin.")
		elif msg == "/approveRequest":
			client.send(b"/approveRequest")
			client.recv(1024).decode("utf-8")
			if username == groups[groupname].admin:
				client.send(b"/proceed")
				usernameToApprove = client.recv(1024).decode("utf-8")
				if usernameToApprove in groups[groupname].joinRequests:
					groups[groupname].joinRequests.remove(usernameToApprove)
					groups[groupname].allMembers.add(usernameToApprove)
					if usernameToApprove in groups[groupname].waitClients:
						groups[groupname].waitClients[usernameToApprove].send(b"/accepted")
						groups[groupname].connect(usernameToApprove,groups[groupname].waitClients[usernameToApprove])
						del groups[groupname].waitClients[usernameToApprove]
					print("Member Approved:",usernameToApprove,"| Group:",groupname)
					client.send(b"User has been added to the group.")
				else:
					client.send(b"The user has not requested to join.")
			else:
				client.send(b"You're not an admin.")
		elif msg == "/disconnect":
			client.send(b"/disconnect")
			client.recv(1024).decode("utf-8")
			groups[groupname].disconnect(username)
			print("User Disconnected:",username,"| Group:",groupname)
			break
		elif msg == "/messageSend":
			client.send(b"/messageSend")
			message = client.recv(1024).decode("utf-8")
			groups[groupname].sendMessage(message,username)
		elif msg == "/waitDisconnect":
			client.send(b"/waitDisconnect")
			del groups[groupname].waitClients[username]
			print("Waiting Client:",username,"Disconnected")
			break
		elif msg == "/allMembers":
			client.send(b"/allMembers")
			client.recv(1024).decode("utf-8")
			client.send(pickle.dumps(groups[groupname].allMembers))
		elif msg == "/onlineMembers":
			client.send(b"/onlineMembers")
			client.recv(1024).decode("utf-8")
			client.send(pickle.dumps(groups[groupname].onlineMembers))
		elif msg == "/changeAdmin":
			client.send(b"/changeAdmin")
			client.recv(1024).decode("utf-8")
			if username == groups[groupname].admin:
				client.send(b"/proceed")
				newAdminUsername = client.recv(1024).decode("utf-8")
				if newAdminUsername in groups[groupname].allMembers:
					groups[groupname].admin = newAdminUsername
					print("New Admin:",newAdminUsername,"| Group:",groupname)
					client.send(b"Your adminship is now transferred to the specified user.")
				else:
					client.send(b"The user is not a member of this group.")
			else:
				client.send(b"You're not an admin.")
		elif msg == "/whoAdmin":
			client.send(b"/whoAdmin")
			groupname = client.recv(1024).decode("utf-8")
			client.send(bytes("Admin: "+groups[groupname].admin,"utf-8"))
		elif msg == "/kickMember":
			client.send(b"/kickMember")
			client.recv(1024).decode("utf-8")
			if username == groups[groupname].admin:
				client.send(b"/proceed")
				usernameToKick = client.recv(1024).decode("utf-8")
				if usernameToKick in groups[groupname].allMembers:
					groups[groupname].allMembers.remove(usernameToKick)
					if usernameToKick in groups[groupname].onlineMembers:
						groups[groupname].clients[usernameToKick].send(b"/kicked")
						groups[groupname].onlineMembers.remove(usernameToKick)
						del groups[groupname].clients[usernameToKick]
					print("User Removed:",usernameToKick,"| Group:",groupname)
					client.send(b"The specified user is removed from the group.")
				else:
					client.send(b"The user is not a member of this group.")
			else:
				client.send(b"You're not an admin.")
		elif msg == "/fileTransfer":
			client.send(b"/fileTransfer")
			filename = client.recv(1024).decode("utf-8")
			if filename == "~error~":
				continue
			client.send(b"/sendFile")
			remaining = int.from_bytes(client.recv(4),'big')
			f = open(filename,"wb")
			while remaining:
				data = client.recv(min(remaining,4096))
				remaining -= len(data)
				f.write(data)
			f.close()
			print("File received:",filename,"| User:",username,"| Group:",groupname)
			for member in groups[groupname].onlineMembers:
				if member != username:
					memberClient = groups[groupname].clients[member]
					memberClient.send(b"/receiveFile")
					with fileTransferCondition:
						fileTransferCondition.wait()
					memberClient.send(bytes(filename,"utf-8"))
					with fileTransferCondition:
						fileTransferCondition.wait()
					with open(filename,'rb') as f:
						data = f.read()
						dataLen = len(data)
						memberClient.send(dataLen.to_bytes(4,'big'))
						memberClient.send(data)
			client.send(bytes(filename+" successfully sent to all online group members.","utf-8"))
			print("File sent",filename,"| Group: ",groupname)
			os.remove(filename)
		elif msg == "/sendFilename" or msg == "/sendFile":
			with fileTransferCondition:
				fileTransferCondition.notify()
		else:
			print("UNIDENTIFIED COMMAND:",msg)
			continue

def handshake(client):
	"""
	It takes a client, gets the username and groupname, and if the groupname is in the groups
	dictionary, it checks if the username is in the group's allMembers set. If it is, it connects the
	client to the group, sends the client a ready message, and starts a new thread for the client. If
	the username is not in the group's allMembers set, it adds the username to the group's joinRequests
	set, adds the client to the group's waitClients dictionary, sends a message to the group that the
	username has requested to join, sends the client a wait message, and starts a new thread for the
	client. If the groupname is not in the groups dictionary, it creates a new group with the username
	as the admin, starts a new thread for the client, sends the client an adminReady message, and prints
	a message to the console
	
	:param client: The socket object
	"""
	username = client.recv(1024).decode("utf-8")
	client.send(b"/sendGroupname")
	groupname = client.recv(1024).decode("utf-8")
	if groupname in groups:
		if username in groups[groupname].allMembers:
			groups[groupname].connect(username,client)
			client.send(b"/ready")
			print("User Connected:",username,"| Group:",groupname)
		else:
			groups[groupname].joinRequests.add(username)
			groups[groupname].waitClients[username] = client
			groups[groupname].sendMessage(username+" has requested to join the group.","PyconChat")
			client.send(b"/wait")
			print("Join Request:",username,"| Group:",groupname)
		threading.Thread(target=pyconChat, args=(client, username, groupname,)).start()
	else:
		groups[groupname] = Group(username,client)
		threading.Thread(target=pyconChat, args=(client, username, groupname,)).start()
		client.send(b"/adminReady")
		print("New Group:",groupname,"| Admin:",username)

def gethost():
	"""
	It starts a ngrok server in the background, waits 3 seconds, then gets the public url of the ngrok
	server and returns the host and port.
	:return: A list of two elements.
	"""
	ngrokServer = threading.Thread(target=os.system,args=("ngrok tcp 8080 >> nul",))
	ngrokServer.start()
	localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
	time.sleep(3)

	tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
	j = json.loads(tunnel_url)

	tunnel_url = j['tunnels'][0]['public_url']  # Do the parsing of the get
	tunnel_url = tunnel_url.replace("tcp://", "")
	return tunnel_url.split(":")


def main():

	clientHost, clientPort = gethost()

	print('█░░░█ █▀▀ █░░ █▀▀ █▀▀█ █▀▄▀█ █▀▀   ▀▀█▀▀ █▀▀█   █▀▀█ █░░█ █▀▀ █░░█ █▀▀█ ▀▀█▀▀')
	print('█▄█▄█ █▀▀ █░░ █░░ █░░█ █░▀░█ █▀▀   ░░█░░ █░░█   █░░█ █▄▄█ █░░ █▀▀█ █▄▄█ ░░█░░')
	print('░▀░▀░ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀░░░▀ ▀▀▀   ░░▀░░ ▀▀▀▀   █▀▀▀ ▄▄▄█ ▀▀▀ ▀░░▀ ▀░░▀ ░░▀░░')
	print('\t\t\t\t\t\t\t\tBy Shivam Singh')



	check_ngrok=input("\nDo you have ngrok Intalled[y/n]: ")

	if check_ngrok=='y':
			host = "127.0.0.1"
			port = 8080
			print(f"Running at HOST:' {clientHost} ' and PORT: ' {clientPort}'")
	elif check_ngrok== 'n':
		print("\nPlz Install Ngrok and add to Environment variable")
		print("Visit http://ngrok.com/signup")
		exit()

	else:
		print("Enter Correct y/n:")

	# print(f"PyChat Server running at {clientHost}:{clientPort}")
	print(f'Share this hostname = "{clientHost}" and port = "{clientPort}"')
	
	listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSocket.bind((host,port))
	listenSocket.listen()
	while True:
		client,_ = listenSocket.accept()
		threading.Thread(target=handshake, args=(client,)).start()

if __name__ == "__main__":
	main()