###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
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
	#def handle_reg(self, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""
		try:
			if(db.CheckNode(p.getAddr(), p.getPort()) == None):
				db.AddDataNode(p.getAddr(), p.getPort())
				self.request.sendall("ACK".encode())
				print("New node inserted")
			else:
				self.request.sendall("DUP".encode())
				print("Node already exists in server")
		except:
			self.request.sendall("NAK".encode())
		nodes = db.GetDataNodes()
		print("Current Nodes in database:")
		print(nodes)

	def handle_list(self, db):
		#Get the file list from the database and send list to client
		try:
			print("Sending List to Client")
			fileList = []
			#Run through files found in the database and store the info in a list of touples
			for fid, file, size in db.GetFiles():
				fileInfo = (fid, file, size)
				fileList.append(fileInfo)
				print(file, size)
			#create a packet to send file info to ls.py
			print("sent")
			ls = Packet()
			ls.BuildListResponse(fileList)
			self.request.sendall(ls.getEncodedPacket().encode())
		except:
			self.request.sendall("NAK".encode())	

	def handle_put(self, db, p):
		#Insert new file into the database and send data nodes to save the file.

		fileInfo = p.getFileInfo()
		print(fileInfo[0], fileInfo[1])
		if db.InsertFile(fileInfo[0], fileInfo[1]):
			# Fill code
			print("File inserted: %s %s" % (fileInfo[0], fileInfo[1]))
			#Send list of datanodes to copy client
			nodeList = Packet()
			nodeList.BuildPutResponse(db.GetDataNodes())
			self.request.sendall(nodeList.getEncodedPacket().encode())
			print("sending Nodes")
			'''''
			result = self.request.recv(1024).decode()
			inode = Packet()
			inode.DecodePacket(result)
			#print(inode.getFileName(), inode.getDataBlocksAfterRecv())
			db.AddBlockToInode(inode.getFileName(), inode.getDataBlocksAfterRecv())
			inodeInfo = db.GetFileInode(inode.getFileName())
			print(inodeInfo)
			'''
		else:
			print("File already exists")
			self.request.sendall("DUP".encode())

	def handle_get(self, db, p):
		#Check if file is in database and return list of server nodes that contain the file.

		# Fill code to get the file name from packet and then 
		# get the fsize and array of metadata server
		
		print("Recieved: ", p.getFileName())
		if db.GetFileInfo(p.getFileName())[0] != None:
			#Return inode to copy client
			inodeInfo = db.GetFileInode(p.getFileName())
			print("inode Info: ", inodeInfo[1], inodeInfo[0])
			#inode = Packet()
			p.BuildGetResponse(inodeInfo[1], inodeInfo[0])
			self.request.sendall(p.getEncodedPacket().encode())
		else:
			self.request.sendall("NFOUND".encode())

	def handle_blocks(self, db, p):
		#Add the data blocks to the file inode
		print("Handling")
		# Fill code to get file name and blocks from
		# packet
		print(p.getFileName(), p.getDataBlocksAfterRecv())
		db.AddBlockToInode(p.getFileName(), p.getDataBlocksAfterRecv())
		inodeInfo = db.GetFileInode(p.getFileName())

		print(inodeInfo)
		# Fill code to add blocks to file inode

	
	def handle(self):

		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		# Define a packet object to decode packet messages
		p = Packet()
		# Receive a msg from the list, data-node, or copy clients
		msg = self.request.recv(1024).decode()
		
		# Decode the packet received
		p.DecodePacket(msg)

		# Extract the command part of the received packet
		cmd = p.getCommand()
		print("Lol: ",cmd)
		# Invoke the proper action 
		if   cmd == "reg":
			# Registration client
			print("Registering Address %s and Port %s" % (p.getAddr(), p.getPort()))
			self.handle_reg(db, p)
			#self.handle_reg(p)

		elif cmd == "list":
			# Client asking for a list of files
			print("sending File names to ls...")
			self.handle_list(db)
		
		elif cmd == "put":
			# Client asking for servers to put data
			print("Asking to Insert File in dfs")
			# Fill code
			self.handle_put(db, p)
		
		elif cmd == "get":
			# Client asking for servers to get data
			print("Asking to Read Data Blocks")
			self.handle_get(db, p)

		elif cmd == "dblks":
			# Client sending data blocks for file
			print("sending Data Blocks")
			self.handle_blocks(db, p)


		db.Close()

if __name__ == "__main__":
    HOST, PORT = "", 8000
    if(len(sys.argv) > 1):
        try:
            PORT = int(sys.argv[1])
        except:
            usage()
            
    server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)
    print(f"Metadata being submissive on {HOST}:{PORT}")
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
