###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	List client for the DFS
#



import socket
import sys
from Packet import *

def usage():
	print ("Usage: python %s <server>:<port, default=8000>" % sys.argv[0])
	sys.exit(0)

def client(ip, port):
	# Contacts the metadata server and ask for list of files.
	print("Cooking %s %s" % (ip, port))
	# Connect to the server
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if ip == 'localhost':
		sock.connect((ip, port))
		print("Connecting to server")
	else:
		sock.connect((int(ip), int(port)))
		print("Connecting to server1")
	#Send request to list files in meta-data.py
	sp = Packet()
	sp.BuildListPacket()
	sock.sendall(sp.getEncodedPacket().encode())
	#Recieve the list of file names with their sizesfrom meta-data.py
	result = Packet()
	msg = sock.recv(1024).decode()
	if(msg != "NAK"):
		result.DecodePacket(msg)
		fileList = result.getFileArray()
		#Print out the list in the packet
		for file, size in fileList:
			print(file, size, "bytes")
	else:
		print("Error: Could not access file list")
	#End connection
	sock.close()


if __name__ == "__main__":

	server = sys.argv[1].split(":")
	
	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 
	
	if(len(sys.argv) == 3):
		ip = sys.argv[1]
		port = sys.argv[2]
	elif(len(server) == 1):
		ip = server[0]
		port = 8000
	elif (len(server) == 2):
		ip = server[0]
		port = int(server[1])

	if not ip:
		usage()

	client(ip, port)
