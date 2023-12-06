###############################################################################
#
# Filename: mds_db.py
# Author: Jose R. Ortiz and and Bernardo A. Bermúdez
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#

import sqlite3

class mds_db:

	def __init__(self, db_name):
		self.c = None
		self.db_name = db_name
		self.conn = None
	
	def Connect(self):
		"""Connect to the database file"""
		try:
			self.conn = sqlite3.connect(self.db_name)
			self.c = self.conn.cursor()
			self.conn.isolation_level = None
			return 1
		except:
			return 0

	def Close(self):
		"""Close cursor to the database"""
		try:
			# self.conn.commit()
			self.c.close() 	
			return 1
		except:
			return 0
	
	def AddDataNode(self, address, port):
		"""Adds new data node to the metadata server
		   Receives IP address and port 
		   I.E. the information to connect to the data node
		"""
          
		query = """insert into dnode (address, port) values (?, ?)"""
		try:
			self.c.execute(query, (address, port))
			return self.c.lastrowid 
		except sqlite3.IntegrityError as e: 
			# print(type(e), dir(e), e)
			if e.args[0].split()[-1].strip() == "unique":
				return 0
			else:
				raise
			
	def CheckNode(self, address, port):
		"""Check if node is in database and returns name, address, port
                   for connection.
		"""
		query = """select nid from dnode where address=? and port=?"""
		try:
			self.c.execute(query, (address, port))
		except:
			return None
		return self.c.fetchone()

	def GetDataNodes(self):
		"""Returns a list of data node tuples (address, port). Useful to know to which 
		   datanodes chunks can be sent.
		"""

		query = """select address, port from dnode where 1"""
		self.c.execute(query)
		return self.c.fetchall()

	def InsertFile(self, fname, fsize):
		"""Create the inode attributes. For this project, the name of the
		   file and its size.
		"""
		query = """insert into inode (fname, fsize) values (?, ?)"""
		try:
			self.c.execute(query, (fname, fsize))
			return 1
		except:
			return 0

	def InsertFileName(self, fname):
		"""Create the inode attributes. For this project, the name of the
		   file and its size.
		"""
		query = """insert into inode (fname) values (?)"""
		try:
			self.c.execute(query, (fname,))
			return 1
		except:
			return 0

	def InsertFileID(self, id, fname, fsize):
		"""Create the inode attributes. For this project, the name of the
		   file and its size.
		"""
		query = """insert into inode (fid, fname, fsize) values (?, ?, ?)"""
		try:
			self.c.execute(query, (id, fname, fsize))
			return 1
		except:
			return 0
 
	def GetFileInfo(self, fname):
		"""Given a filename, if the file is stored in DFS,
		   return its filename id and fsize. Internal use only.
		   Does not have to be accessed from the metadata server.
		"""
		query = """select fid, fsize from inode where fname=?"""
		try:
			self.c.execute(query, (fname,))
			result = self.c.fetchone()
			return result[0], result[1]
		except:
			return None, None

	def GetFiles(self):
		"""Returns the attributes of the files stored in the DFS.
		   File Name and Size.
		"""

		query = """select fname, fsize from inode where 1"""
		self.c.execute(query)
		return self.c.fetchall()

	def AddBlockToInode(self, fname, blocks):
		"""Once the Inode was created with the file's attribute
		   and the data copied to the data nodes. The inode is 
		   updated to point to the data blocks. So this function receives
		   the filename and a list of tuples with (node id, chunk id)
		"""
		fid, dummy1 = self.GetFileInfo(fname)
		if not fid:
			return None
		for address, port, chunkid in blocks:
			nid = self.CheckNode(address, port)
			if nid:
				query = """insert into block (nid, fid, cid) values (?, ?, ?)"""
				self.c.execute(query, (nid[0], fid, chunkid))
			else:
				return 0 
		return 1

	def GetFileInode(self, fname):
		"""Knowing the file name, this function returns the whole Inode information.
		   I.E. Attributes and the list of data blocks with all the information to access 
		   the blocks (node name, address, port, and the chunk of the file).
		"""

		fid, fsize = self.GetFileInfo(fname)
		if not fid:
			return None, None
		query = """select address, port, cid from dnode, block where dnode.nid = block.nid and block.fid=?"""
		self.c.execute(query, (fid,))
		return fsize, self.c.fetchall()