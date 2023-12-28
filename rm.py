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
	print("Usage:\n\tFrom DFS: python3 %s <server>:<port>:<dfs file path>" % (sys.argv[0]))
	sys.exit(0)
	
def rmFromDFS(address, fname):
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
	inode.BuildRmPacket(fname) # Should be BuildRemovePacket(fname)
	sockMeta.send(inode.getEncodedPacket().encode())
	
	# Recieving Inode Information
	result = sockMeta.recv(1024).decode()
	if(result == "NFOUND"):
		print("File not found in file system")
		
	else:
		print("mulch gang 4 life")
		
        # If there is no error response, retreive file data blocks and attributes
		inode.DecodePacket(result)
		blockList = inode.getDataBlocks() # Data Blocks
		size = inode.getFileInfo()[1] # File Size
		print(size, blockList)

		# Deleting data blocks of file process
		nodeCount = 0 # Tracks amount of blocks recieved by datanodes
		for nodeIp, nodePort, blockId in blockList:

			# Connecting to current datanode
			sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if nodeIp == 'localhost':
				sockNode.connect((nodeIp, nodePort))
			else:
				sockNode.connect((int(nodeIp), int(nodePort)))
	
			# Send block id to datanode  
			block = Packet()
			block.BuildRmDataBlockPacket(blockId)
			sockNode.send(block.getEncodedPacket().encode())

			# End of connection with current datanode
			nodeCount += 1
			sockNode.close()

	# File successfully reconstructed, end copy to file system process
	sockMeta.close()


if __name__ == "__main__":
#	client("localhost", 8000)
	if len(sys.argv) < 2:
		usage()

	file_from = sys.argv[1].split(":")

 	# Si no tiene directory de destination pues se asume que se colocara en...
	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		print((ip, port), from_path)
		rmFromDFS((ip, port), from_path)

	else:
		print("Error: incorrect format")
		usage()

		


