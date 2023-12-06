###############################################################################
#
# Filename: data-node.py
# Author: Jose R. Ortiz and Bernardo A. Bermúdez
#
# Description:
# 	data node server for the DFS
#

from Packet import *

import sys
import socket
import socketserver
import uuid
import os.path

def usage():
	print ("Usage: python %s <server> <port> <data path> <metadata port,default=8000>" % sys.argv[0])
	sys.exit(0)


def register(meta_ip, meta_port, data_ip, data_port):
	"""Creates a connection with the metadata server and
	   register as data node
	"""
 
	# Connect to metadata
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if meta_ip == 'localhost':
		sock.connect((meta_ip, meta_port))
	else:
		sock.connect((int(meta_ip), int(meta_port)))

	try:
		response = "NAK"
		sp = Packet()
		while response == "NAK":
      
			# Send registration request to metadata server
			sp.BuildRegPacket(data_ip, data_port)
			sock.sendall(sp.getEncodedPacket().encode())

			# Recieves answer from metadata server
			response = sock.recv(1024).decode()
			if response == "ACK":
				
				# registrated for the first time in metadata server
				print("registered datanode in metadata server")
				print("Connected to metadata server from %s:%s" % (sp.getAddr(), sp.getPort()))
			if response == "DUP":
       
				# re-connected to metadata server
				print("Connected to metadata server from %s:%s" % (sp.getAddr(), sp.getPort()))
			if response == "NAK":
       
				# could not connect to metadata server
				print("Registratation Error")

	# After metadata response, end of registration process
	finally:
		sock.close()

class DataNodeTCPHandler(socketserver.BaseRequestHandler):

	def handle_put(self, p):
		"""Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""
  
		# Directory were blocks will be stored
		DATA_PATH = sys.argv[3]
		if(DATA_PATH == "."):
			DATA_PATH = ""
		elif(DATA_PATH[len(DATA_PATH)-1] != '/' ):
			DATA_PATH += '/'

		# Recieves filesize from copy client
		chunkSize = p.getBlockSize()
  
		# Lets copy client know that metadata is ready to recieve memory chunk
		self.request.sendall("OK".encode())
		
		# Generates an unique block id to know were chunk will be stored
		blockid = str(uuid.uuid1())
  
		# Putting memory block process
		with open(DATA_PATH + blockid, 'wb') as destinationFile:
			
			# Recieving chunk from copy client between pieces to avoid missing data
			count = 0
			while(count < chunkSize):
				chunk = self.request.recv(min(4096, chunkSize - count))
				if not chunk:
					break
				destinationFile.write(chunk)
				count += len(chunk)

		# Sending block id to copy client
		sendBlockID = Packet()
		sendBlockID.BuildGetDataBlockPacket(blockid)
		self.request.sendall(sendBlockID.getEncodedPacket().encode())
		
	def handle_get(self, p):
		"""Retrieves block from respective blockid for copy client"""		
  
		# Directory were blocks should be stored
		DATA_PATH = sys.argv[3]
		if(DATA_PATH == "."):
			DATA_PATH = ""
		elif(DATA_PATH[len(DATA_PATH)-1] != '/' ):
			DATA_PATH += '/'
   
		# Get the block id from the packet
		blockid = p.getBlockID()
		
		# Checks if memory block in dfs
		if os.path.isfile(DATA_PATH + blockid):
      
			# Aquires size of chunk
			fileStat = os.stat(DATA_PATH + blockid)
			blockSize = fileStat.st_size
   
			# Access block of memory in file
			blockFile = open(DATA_PATH + blockid, 'rb')

			# Lets copy client know that the datanode is ready to send block
			self.request.sendall("OK".encode())
   
			# Checks if copy client is ready to recieve memory block
			result = self.request.recv(1024).decode()
			if(result == "READY"):
       
				# Sending memory block in in pieces to avoid memory loss
				count = 0
				while(count < blockSize):
					chunk = blockFile.read(4096)
					if not chunk:
						self.request.send()
						break
					self.request.send(chunk)
					count += len(chunk)
   
		else:
			self.request.sendall("NAK".encode())
  

	def handle(self):
		"""recieves packet from copy client and invoke the proper action from it"""
  
		#recieves new command package
		msg = self.request.recv(1024).decode()
		p = Packet()
		p.DecodePacket(msg)

		cmd = p.getCommand() # Command from packet
  
		# Invoke the proper action 
		if cmd == "put":
			# Register new data blocks
			self.handle_put(p)

		elif cmd == "get":
			# Get data blocks
			self.handle_get(p)

if __name__ == "__main__":

	#Validation of arguments
	META_PORT = 8000
	if len(sys.argv) < 4:
		usage()

	try:
		HOST = sys.argv[1]
		PORT = int(sys.argv[2])
		DATA_PATH = sys.argv[3]

		if len(sys.argv) > 4:
			META_PORT = int(sys.argv[4])

		if not os.path.isdir(DATA_PATH):
			print ("Error: Data path %s is not a directory." % DATA_PATH)
			usage()
	except:
		usage()

	# Initiate Registration Process
	register("localhost", META_PORT, HOST, PORT)
 
	# Initiate datanode server
	server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)

    # Program interrupted (Ctrl-C)
	server.serve_forever()
