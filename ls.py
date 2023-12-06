###############################################################################
#
# Filename: ls.py
# Author: Jose R. Ortiz and Bernardo A. Bermúdez
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
	"""Contacts the metadata server and ask for list of files"""
 
	#Connecting to metadata
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if ip == 'localhost':
		sock.connect((ip, port))
	else:
		sock.connect((int(ip), int(port)))

	#Send request to recieve file list from meta-data server
	sp = Packet()
	sp.BuildListPacket()
	sock.sendall(sp.getEncodedPacket().encode())

	#Recieve the list of file names and attributes from meta-data server
	result = Packet()
	msg = sock.recv(1024).decode()

	#Checking if list was sent 
	if(msg != "NAK"):
	
		#Reveal list of files
		result.DecodePacket(msg)
		fileList = result.getFileArray()

		#Display files from list
		for file, size in fileList:
			print(file, size, "bytes")
	else:
		print("Error: Could not access file list")

	#End of ls process
	sock.close()


if __name__ == "__main__":

	server = sys.argv[1].split(":")
	
	#Validation of arguments
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

	#Begin ls process
	client(ip, port)
