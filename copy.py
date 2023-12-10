###############################################################################
#
# Filename: copy.py
# Author: Jose R. Ortiz and Bernardo A. Bermúdez
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
	else:
		sockMeta.connect((int(metaIp), int(metaPort)))
	
	# Checks if source file exists
	if os.path.isfile(path):
     
		# Aquires attributes from source file
		fileStat = os.stat(path)
		size = fileStat.st_size
  
		# Create a Put packet to send to the metadata server
		fileInfo = Packet()
		fileInfo.BuildPutPacket(fname, size)
		sockMeta.send(fileInfo.getEncodedPacket().encode())

		# Recieve list of data-nodes info from metadata server
		response = sockMeta.recv(1024).decode()
		sockMeta.close()

		# File does not exist in database
		if(response == "DUP"):
			print("Name already in use in file system")
		else:
			# Recieve list of data-node info from meta-data server
			nodeList = Packet()
			nodeList.DecodePacket(response)

			# Storing file memory in dfs process 
			blockList = [] # Stores the block information of each chunk of the file
			chunkSize = size//len(nodeList.getDataNodes()) # Fraction of file memory each datanode will recieve
			sourceFile = open(path, 'rb') # File that will be copied in dfs
			nodeCount = 0 # Tracks amount of dataNodes that recieved the chunk
			for address, port in nodeList.getDataNodes():

				# Takes consideration the remaining bits in the last chunk
				if(nodeCount < len(nodeList.getDataNodes())-1):
					size -= chunkSize
				else:
					chunkSize = size
	
				# Connecting to current data-node
				sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if address == 'localhost':
					sockNode.connect((address, port))
				else:
					sockNode.connect((int(address), int(port)))

				# Sending get packet with chunk size to inode
				fileChunk = Packet()
				fileChunk.BuildPutBlockSize(chunkSize)
				sockNode.send(fileChunk.getEncodedPacket().encode())
	
				# Recieving signal that datanode is ready to recieve chunk
				response = sockNode.recv(1024).decode()
				if(response == "OK"):
					
					# Sending chunks to datanode between pieces to avoid missing data
					count = 0
					while(count < chunkSize):
						chunk = sourceFile.read(min(4096, chunkSize - count))
						if not chunk:
							break
						sockNode.send(chunk)
						count += len(chunk)
					chunkSize = count
				
				# Recieving block id where datanode stored the file memory chunk
				response = sockNode.recv(1024).decode()
				blockid = Packet()
				blockid.DecodePacket(response)
				
				# Storing block info
				blockList.append((address, port, blockid.getBlockID()))

				# End of connection with current datanode
				nodeCount += 1
				sockNode.close()
	
			# Reconnect with Meta-data server
			sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if metaIp == 'localhost':
				sockMeta.connect((metaIp, metaPort))
			else:
				sockMeta.connect((int(metaIp), int(metaPort)))
    
			# Send inode information, block list and file name, to the metadata server
			inode = Packet()
			inode.BuildDataBlockPacket(fname, blockList)
			sockMeta.send(inode.getEncodedPacket().encode())

			# File successfully copied to dfs, end copy to dfs process 
			sockMeta.close()
	else:
		print("File not Found")	
	
def copyFromDFS(address, fname, path):
	""" Contact the metadata server to ask for the file blocks of
	    the file fname.  Get the data blocks from the data nodes.
	    Saves the data in path.
	"""
 
   	# Connect to metadata server
	sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if address[0] == 'localhost':
		sockMeta.connect((address[0], address[1]))
	else:
		sockMeta.connect((int(address[0]), int(address[1])))
	
 	# Sending request to recieve inode information of source file
	inode = Packet()
	inode.BuildGetPacket(fname)
	sockMeta.send(inode.getEncodedPacket().encode())
	
	# Recieving Inode Information
	result = sockMeta.recv(1024).decode()
	if(result == "NFOUND"):
		print("File not found in file system")
	else:

		# If there is no error response, retreive file data blocks and attributes
		inode.DecodePacket(result)
		blockList = inode.getDataBlocks() # Data Blocks
		size = inode.getFileInfo()[1] # File Size

		# Retrieving file memory from dfs process
		chunkSize = size // len(blockList) # Bit size of chunks sent by datanodes
		destinationFile = open(path, 'wb') # File where file memory will be reconstructed
		nodeCount = 0 # Tracks amount of blocks recieved by datanodes
		for nodeIp, nodePort, blockId in blockList:
	
			# Takes consideration the remaining bits in the last block
			if(nodeCount < len(blockList)-1):
				size -= chunkSize
			else:
				chunkSize = size

			# Connecting to current datanode
			sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if nodeIp == 'localhost':
				sockNode.connect((nodeIp, nodePort))
			else:
				sockNode.connect((int(nodeIp), int(nodePort)))
	
			# Send block id to datanode  
			block = Packet()
			block.BuildGetDataBlockPacket(blockId)
			sockNode.send(block.getEncodedPacket().encode())

			# Checks if datanode contains the memory chunk of file 
			result = sockNode.recv(1024).decode()
			if(result != "OK"):
				
				# Send error message and terminate copy process
				print("Error: Memory not found in nfs data")
				sockNode.close()
				exit()
			else:
	
				# Lets datanode know that its ready to recieve memory chunk
				sockNode.send("READY".encode())
	
				# Recieving chunk from datanode between pieces to avoid missing data
				count = 0
				while(count < chunkSize):
					chunk = sockNode.recv(4096)
					if not chunk:
						break
					destinationFile.write(chunk)
					count += len(chunk)

			# End of connection with current datanode
			nodeCount += 1
			sockNode.close()

	# File successfully reconstructed, end copy to file system process
	sockMeta.close()

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
		elif(os.path.isfile(to_path)):
			print("Error: file name %s is already taken." % to_path)
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


