###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and Bernardo A. Bermúdez
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#
# Please modify globals with appropiate info.

#from _socket import _RetAddress
#from socketserver import _RequestType, BaseServer
from mds_db import *
from Packet import *
import sys
import socketserver

def usage():
	print ("Usage: python %s <port, default=8000>" % sys.argv[0])
	sys.exit(0)

class MetadataTCPHandler(socketserver.BaseRequestHandler):
	def handle_reg(self, db, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""
		try:
			#Checking if data-node exists in database
			if(db.CheckNode(p.getAddr(), p.getPort()) == None):
       
				#Registering data-node to database
				db.AddDataNode(p.getAddr(), p.getPort())
				self.request.send("ACK".encode())
			else:
				self.request.send("DUP".encode())
		except:
			self.request.send("NAK".encode())

	def handle_list(self, db):
		"""Gets the file list from the database and send list to ls client"""
		try:
			fileList = [] # Stores File info in tuples

			# Run through files found in the database and store the info in the list
			for file, size in db.GetFiles():
				fileInfo = (file, size)
				fileList.append(fileInfo)

			# Sending file list to ls client
			ls = Packet()
			ls.BuildListResponse(fileList)
			self.request.send(ls.getEncodedPacket().encode())
		except:
			self.request.send("NAK".encode())	

	def handle_put(self, db, p):
		"""Inserts file into data base and returns list of data-nodes to copy client"""
  
		# Retrieving file info from packet
		fileInfo = p.getFileInfo()
  
		# Inserting new file into database or tells client that file name is already in use
		if db.InsertFile(fileInfo[0], fileInfo[1]):
   
			#Sending list of data-nodes to copy client
			nodeList = Packet()
			nodeList.BuildPutResponse(db.GetDataNodes())
			self.request.send(nodeList.getEncodedPacket().encode())
		else:
			self.request.send("DUP".encode())

	def handle_get(self, db, p):
		"""Checks if file is in database and returns inode information"""
		
		#Cheking if file exists
		if db.GetFileInfo(p.getFileName())[0] != None:
      
			#Return inode to copy client
			inodeInfo = db.GetFileInode(p.getFileName())
			p.BuildGetResponse(inodeInfo[1], inodeInfo[0])
			self.request.send(p.getEncodedPacket().encode())
		else:
			self.request.send("NFOUND".encode())

	def handle_blocks(self, db, p):
		"""Adds the data blocks to the file inode"""

		# Storing inode information in metadata server
		db.AddBlockToInode(p.getFileName(), p.getDataBlocks())

	def handle_rm(self, db, p):
		"""
		Checks if file is in database, returns inode information to client and 
		deletes file record in database
		"""
		
		# Cheking if file exists
		if db.GetFileInfo(p.getFileName())[0] != None:
			print("File found")
			# Return inode to rm client
			inodeInfo = db.GetFileInode(p.getFileName())
			p.BuildGetResponse(inodeInfo[1], inodeInfo[0])
			self.request.send(p.getEncodedPacket().encode())

			# Deleting file from database
			db.DeleteFile(p.getFileName())

		else:
			print("File NOT found")
			self.request.send("NFOUND".encode())
	
	def handle(self):

		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		#packet object to decode packet messages
		p = Packet()
		msg = self.request.recv(1024).decode()
		p.DecodePacket(msg)

		# Extract the command part of the received packet
		cmd = p.getCommand()
  
		print(cmd)
		print(p.getFileName())

		# Invoke the proper action 
		if   cmd == "reg":
			# Registration client
			self.handle_reg(db, p)

		elif cmd == "list":
			# ls client asking for a list of files
			self.handle_list(db)
		
		elif cmd == "put":
			# copy client asking for servers to put data
			self.handle_put(db, p)
		
		elif cmd == "get":
			# copy client asking for servers to get data
			self.handle_get(db, p)

		elif cmd == "dblks":
			# copy client sending data blocks for file
			self.handle_blocks(db, p)

		elif cmd == "rm":
			# rm client asking for removing a file
			self.handle_rm(db, p)

		db.Close()

if __name__ == "__main__":
    HOST, PORT = "", 8000
	#Checking for correct arguments
    if(len(sys.argv) > 1):
        try:
            PORT = int(sys.argv[1])
        except:
            usage()
    
    #Initiate metadata server
    server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)
    print(f"Metadata running {HOST}:{PORT}")

    # Program interrupted (Ctrl-C)
    server.serve_forever()
