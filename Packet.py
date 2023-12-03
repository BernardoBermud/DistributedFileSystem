###############################################################################
#
# Filename: Packet.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
# 	Packet creation support library for the DFS project. Database info for
#
# Please modify globals with appropiate info.

import json

class Packet:

	def __init__(self):
	
		self.commands = ["reg", "list", "put", "get", "dblks"]
		self.packet = {}
	
	#USADO
	def getEncodedPacket(self):
		"""returns a seriliazed packet ready to send through the network.  
		First you need to build the packets.  See BuildXPacket functions."""

		return json.dumps(self.packet) 

	#USADO
	def getCommand(self):
		"""Returns the command type of a packet"""
		return self.packet.get("command")

	#USADO: Insertar nuevo data-Node a Meta-data
	def getAddr(self):
		"""Returns the IP address of a server""" 
		return self.packet.get("addr")

	#USADO: Insertar nuevo data-Node a Meta-data
	def getPort(self):
		"""Returns the port number of a server"""
		return self.packet.get("port")

	def DecodePacket(self, packet):
		"""Receives a serialized message and turns it into a packet object."""
		self.packet = json.loads(packet)

	#USADO: data-node enviar su info al meta-data para que lo registre
	def BuildRegPacket(self, addr, port):
		"""Builds a registration packet"""
		self.packet = {"command": "reg", "addr": addr, "port": port}
		
	#USADO: Request de ls
	def BuildListPacket(self):
		"""Builds a list packet for file listing"""

		self.BuildCommand("list")

	#USADO: lo que Meta-data le devuelve a ls 
	def BuildListResponse(self, lfiles):
		"""Builds a list response packet"""

		self.packet = {"files": lfiles}	

	#USADO: para ls desplegar lista de files recibida del meta-data
	def getFileArray(self):
		"""Builds a list response packet"""
		return self.packet.get("files")

	def BuildGetPacket(self, fname):
		"""Build a get packet to get fname."""
		self.BuildCommand("get")
		self.packet["fname"] = fname

	#USADO: Lo que copy le envía al meta-data para insertar nuevo archivo
	def BuildPutPacket(self, fname, fsize):
		"""Builds a put packet to put fname and file size."""
		self.BuildCommand("put")
		self.packet["fname"] = fname
		self.packet["fsize"] = fsize

	#lo que copy le va a enviar al metadata server (inode)
	def BuildDataBlockPacket(self, fname, block_list):
		"""Builds a data block packet. Contains the file name and the list of blocks for the file"""
		self.BuildCommand("dblks")
		self.packet["blocks"] = block_list
		self.packet["fname"] = fname

	#lo que el copy le envía al data node despued de recibir el inode del metadata
	def BuildGetDataBlockPacket(self, blockid):
		"""Builds a get data block packet. Usefull when requesting a data block to a data node."""

		self.BuildCommand("get")
		self.packet["blockid"] = blockid

	def getBlockID(self):
		"""Returns a the block_id from a packet."""
		return self.packet.get("blockid")

	#USADO: meta-data despliega los valores del file enviado por el copy
	def getFileInfo(self):
		"""Returns the file info in a packet."""
		return self.packet.get("fname"), self.packet.get("fsize") 

	
	def getFileName(self):
		"""Returns the file name in a packet."""
		return self.packet.get("fname") 

	def BuildGetResponse(self, metalist, fsize):
		"""Builds a list of data node servers with the blocks of a file, and file size."""
		self.packet["servers"] = metalist
		self.packet["fsize"] = fsize

	#USADO: mata-data crea una lista de los data-nodes para enviarsela al copy
	def BuildPutResponse(self, metalist):
		"""Builds a list of data node servers where a file data blocks can be stored.
		I.E. a list of available data servers."""
		self.packet["servers"] = metalist

	#USADO: Copy depliega listado de data-nodes redibida por el metadata
	def getDataNodes(self):
		"""Returns a list of data servers"""
		return self.packet.get("servers")

	def getDataBlocks(self):
		"""Returns a list of data blocks""" 
		return self.packet.get("blocks")

	def BuildCommand(self, cmd):
		"""Builds a packet type"""
		if cmd in self.commands:
			self.packet = {"command": cmd}
   
   #Funciones Custom

	def BuildFileChunk(self, chunk):
		"""Builds a chunk of memory of a file"""
		self.BuildCommand("put")
		self.packet["chunk"] = chunk
  
	def getFileChunk(self):
		"""Returns chunk of memory of a file"""
		return self.packet.get("chunk")



		
	
		
		
