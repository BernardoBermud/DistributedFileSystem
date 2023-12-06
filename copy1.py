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
	else:
		sockMeta.connect((int(metaIp), int(metaPort)))
	
	# Makes sure source file exists
	if os.path.isfile(path):
     
		#Aquires attributes from source file
		fileStat = os.stat(path)
		size = fileStat.st_size
  
		# Create a Put packet with the fname and the length of the data
		fileInfo = Packet()
		fileInfo.BuildPutPacket(fname, size)
		sockMeta.sendall(fileInfo.getEncodedPacket().encode())

		# Recieve list of data-nodes info from meta-data server
		response = sockMeta.recv(1024).decode()
		sockMeta.close()

		# File does not exist in database
		if(response == "DUP"):
			print("Name already in use in file system")
		else:
      
			# Recieve list of data-node info from meta-data server
			nodeList = Packet()
			nodeList.DecodePacket(response)
   
			#Dividing the memory into chunks and safe them in a list
			#chunkSize = size//len(nodeList.getDataNodes())
			
			# chunks = [] #Contains tuples of the memory Chunk and the chunk size
			# with open(path, 'rb') as sourceFile:
			# 	while True:
        
			# 		#makes sure that all bits are sent and avoid consequenses of integer division
			# 		if(size > chunkSize):
			# 			size -= chunkSize
			# 		else:
			# 			chunkSize = size
      
			# 		#reads portion of memory
			# 		chunk = sourceFile.read(chunkSize)
			# 		if not chunk:
			# 			break
  
			# 		#saves chunk and chunk size in list
			# 		chunks.append((chunk, chunkSize))

			#Sending part of file to each data-node and recieving a unique id where the piece of the file is stored.
			blockList = [] #Will store the block information of each chunk of the file
			chunkSize = size//len(nodeList.getDataNodes())
			sourceFile = open(path, 'rb')
			for address, port in nodeList.getDataNodes():
				try:
					#Getting the current chunk and the chunk size from the list
					if(size > chunkSize):
						size -= chunkSize
					else:
						chunkSize = size
		
					#Connecting to current data-node
					sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					if address == 'localhost':
						sockNode.connect((address, port))
					else:
						sockNode.connect((int(address), int(port)))

					#Sending get packet with chunk size to inode
					fileChunk = Packet()
					fileChunk.BuildPutFileChunk(chunkSize)
					sockNode.sendall(fileChunk.getEncodedPacket().encode())
		
					#Recieving signal that data-node is ready to recieve chunk and sending it
					response = sockNode.recv(1024).decode()
					if(response == "OK"):
						count = 0
						while(count < chunkSize):
							chunk = sourceFile.read(4096)
							if not chunk:
								sockNode.send()
								break
							sockNode.send(chunk)
							count += len(chunk)
					
					#Recieving uuid where data-node stored the file memory chunk
					response = sockNode.recv(1024).decode()
					chunkID = Packet()
					chunkID.DecodePacket(response)
					
					#Storing block info
					blockList.append((address, port, chunkID.getBlockID()))

					#End of connection between data-node and client
					sockNode.close()
				except:
					print("Error: Sending Memory Process Failed")
	
			# Reconnect with Meta-data server
			sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if metaIp == 'localhost':
				sockMeta.connect((metaIp, metaPort))
			else:
				sockMeta.connect((int(metaIp), int(metaPort)))
    
			#Create the inode utilizing the block list and file name and send it to the meta-data server
			inode = Packet()
			inode.BuildDataBlockPacket(fname, blockList)
			sockMeta.sendall(inode.getEncodedPacket().encode())

			#End copy to dfs process 
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
	sockMeta.sendall(inode.getEncodedPacket().encode())
	
	#Recieving Inode Information
	result = sockMeta.recv(1024).decode()
	if(result == "NFOUND"):
		print("File not found in file system")
	else:
     
		# If there is no error response, retreive file data blocks and attributes
		inode.DecodePacket(result)
		blockList = inode.getDataBlocksAfterRecv() # Data Blocks
		size = inode.getFileInfo()[1] # File Size

		#Calling each of the datanodes to retrieve the chunks of memory using blockid
		chunkSize = size // len(blockList) # Bit size of chunks sent by datanodes
		chunks = [] # Were memory chunks will be stored 
		destinationFile = open(path, 'wb')
		for nodeIp, nodePort, blockId in blockList:
			
			# Makes sure that all bits are sent and avoid consequenses of integer division
			if(size > chunkSize):
				size -= chunkSize
			else:
				chunkSize = size

			# Connecting to current datanode
			sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if nodeIp == 'localhost':
				sockNode.connect((nodeIp, nodePort))
			else:
				sockNode.connect((int(nodeIp), int(nodePort)))
    
			#Send block id to datanode  
			block = Packet()
			block.BuildGetDataBlockPacket(blockId)
			sockNode.sendall(block.getEncodedPacket().encode())

			# Checks if datanode contains the memory chunk of file 
			result = sockNode.recv(1024).decode()
			if(result != "OK"):
				print("Error: Memory not found in nfs data")
				sockNode.close()
				exit()
			else:
       
				# Lets datanode know that its ready to recieve memory chunk
				sockNode.sendall("READY".encode())
    
				#recieve file chunk and insert it in chunk list
				count = 0
				while(count < chunkSize):
					chunk = sockNode.recv(4096)
					if not chunk:
						break
					destinationFile.write(chunk)
					count += len(chunk)
   
			#End of connection between current datanode and client
			sockNode.close()
   
		#generate new file were file will be reconstructed with the chunks of the datalist
		# with open(path, 'wb') as destination_file:
		# 	for chunk in chunks:
		# 		destination_file.write(chunk)

	#End copy to file system process
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


