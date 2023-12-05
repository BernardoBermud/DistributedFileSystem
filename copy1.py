###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	Copy client for the DFS
#
#
###############################################################################

import socket
import sys
import os.path

from Packet import *

def usage():
	print("Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>\n\tTo   DFS: python %s <source file> <server>:<port>:<dfs file path>" % (sys.argv[0], sys.argv[0]))
	sys.exit(0)

def copyToDFS(address, fname, path):
	""" Contact the metadata server to ask to copu file fname,
	    get a list of data nodes. Open the file in path to read,
	    divide in blocks and send to the data nodes. 
	"""

	# Create a connection to the data server
	metaIp = address[0]
	metaPort = address[1]
	sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if metaIp == 'localhost':
		sockMeta.connect((metaIp, metaPort))
		print("Connecting to server")
	else:
		sockMeta.connect((int(metaIp), int(metaPort)))
		print("Connecting to server1")
	
	# Read file
	if os.path.isfile(path):
		fileStat = os.stat(path)
		size = fileStat.st_size
		# Create a Put packet with the fname and the length of the data,
		# and sends it to the metadata server 
		fileInfo = Packet()
		fileInfo.BuildPutPacket(fname, size)
		sockMeta.sendall(fileInfo.getEncodedPacket().encode())
		print("File Sent")
		response = sockMeta.recv(1024).decode()
		#Va a recibir del metadata un mensage de que esta duplicado o el packet conteniendo los ports.
		if(response == "DUP"):
			print("Name already in use in file system")
		else:
			#Recieve list of data-node info from meta-data server
			# Get the list of data nodes.
			nodeList = Packet()
			nodeList.DecodePacket(response)
			print(nodeList.getDataNodes())

			blockList = [] #Will store the block information of each chunk of the file
			#Sending part of file to each data-node and recieving a unique id where the piece of the file is stored.
			for address, port in nodeList.getDataNodes():
				#Connecting to current data-node
				sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if address == 'localhost':
					sockNode.connect((address, port))
					print("Connecting to Data-Node %s" % (port))
				else:
					sockNode.connect((int(address), int(port)))
					print("Connecting to Data-Node %s" % (port))
     
				#Sending file memory chunk packet to data-node
				fileChunk = Packet()
				fileChunk.BuildPutFileChunk("It's a me, Mario!")
				sockNode.sendall(fileChunk.getEncodedPacket().encode())

				#Recieving uuid where data-node stored the file memory chunk
				response = sockNode.recv(1024).decode()
				chunkID = Packet()
				chunkID.DecodePacket(response)
				
				#Storing block info
				blockList.append((address, port, chunkID.getBlockID()))

				#End of connection between data-node and client
				sockNode.close()
    
			sockMeta.close()
			sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if metaIp == 'localhost':
				sockMeta.connect((metaIp, metaPort))
				print("Connecting to server")
			else:
				sockMeta.connect((int(metaIp), int(metaPort)))
				print("Connecting to server1")
			#Create the inode utilizing the block list and fine name and send it to the meta-data server
			inode = Packet()
			inode.BuildDataBlockPacket(fname, blockList)
			print(inode.getFileName(), inode.getDataBlocks())
			sockMeta.sendall(inode.getEncodedPacket().encode())
	else:
		print("File not Found")	

	# If no error or file exists
	# Get the list of data nodes.
	# Divide the file in blocks
	# Send the blocks to the data servers

	# Fill code	

	# Notify the metadata server where the blocks are saved.

	# Fill code
 
	#End of process
	sockMeta.close()
	
def copyFromDFS(address, fname, path):
	""" Contact the metadata server to ask for the file blocks of
	    the file fname.  Get the data blocks from the data nodes.
	    Saves the data in path.
	"""
	print("Metadata Address: ", address[0])
	print("Metadata Port: ", address[1])
	print("Where File is in dfs", fname)
	print("Name of file output: ", path)
 
   	# Contact the metadata server to ask for information of fname
	sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if address[0] == 'localhost':
		sockMeta.connect((address[0], address[1]))
		print("Connecting to server")
	else:
		sockMeta.connect((int(address[0]), int(address[1])))
		print("Connecting to server1")
	
 	#Sending request to recieve inode information
	inode = Packet()
	inode.BuildGetPacket(fname)
	sockMeta.sendall(inode.getEncodedPacket().encode())
 
	#Recieving Inode Information
	result = sockMeta.recv(1024).decode()
	if(result == "NFOUND"):
		print("File not found in file system")
	else:
		# If there is no error response Retreive the data blocks
		print(result)
		inode.DecodePacket(result)
		blockList = inode.getDataBlocksAfterRecv() #Data Blocks
		fSize = inode.getFileInfo()[1]#File Size

		#Calling each of the data nodes to retrieve the chunks of memory 
		for nodeIp, nodePort, blockId in blockList:
			sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if nodeIp == 'localhost':
				sockNode.connect((nodeIp, nodePort))
				print("Connecting to Data-Node %s" % (nodePort))
			else:
				sockNode.connect((int(nodeIp), int(nodePort)))
				print("Connecting to Data-Node %s" % (nodePort))
    
			block = Packet()
			block.BuildGetDataBlockPacket(blockId)
			sockNode.sendall(block.getEncodedPacket().encode())
   
			result = sockNode.recv(1024).decode()
			block.DecodePacket(result)
			print(block.getFileChunk())
   
			sockNode.close()


			

	# Fill code

    	# Save the file
	
	# Fill code

if __name__ == "__main__":
#	client("localhost", 8000)
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")

 	#Si no tiene directory de destination pues se asume que se colocara en...
	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print("Error: path %s is a directory.  Please name the file." % to_path)
			usage()

		copyFromDFS((ip, port), from_path, to_path)

	elif len(file_to) > 2:
		ip = file_to[0]
		port = int(file_to[1])
		to_path = file_to[2]
		from_path = sys.argv[1]

		if os.path.isdir(from_path):
			print ("Error: path %s is a directory.  Please name the file." % from_path)
			usage()

		copyToDFS((ip, port), to_path, from_path)


