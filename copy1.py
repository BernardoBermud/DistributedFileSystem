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
	
	sockMeta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if address[0] == 'localhost':
		sockMeta.connect((address[0], address[1]))
		print("Connecting to server")
	else:
		sockMeta.connect((int(address[0]), int(address[1])))
		print("Connecting to server1")
	
	# Read file
	if os.path.isfile(path):
		fileStat = os.stat(path)
		size = fileStat.st_size
		# Create a Put packet with the fname and the length of the data,
		# and sends it to the metadata server 
		fileInfo = Packet()
		fileInfo.BuildPutPacket(path, size)
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

			#Sending part of file to each data-node and recieving a unique id where the piece of the file is stored.
			for address, port in nodeList.getDataNodes():
				sockNode = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if address == 'localhost':
					sockNode.connect((address, port))
					print("Connecting to Data-Node %s" % (port))
				else:
					sockNode.connect((int(address), int(port)))
					print("Connecting to Data-Node %s" % (port))
     
				testMessage = "It's a me, Mario!"
				sockNode.sendall(testMessage.encode())
    
				message = sockNode.recv(1024).decode()
				print(message)
				sockNode.close()
			# Divide the file in blocks
			# Send the blocks to the data servers
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

   	# Contact the metadata server to ask for information of fname

	# Fill code

	# If there is no error response Retreive the data blocks

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


