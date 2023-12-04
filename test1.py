###############################################################################
#
# Filename: test.py
# Author: Jose R. Ortiz and ... (hopefully some students contribution)
#
# Description:
#       Script to test the MySQL support library for the DFS project.
#
#

# This is how to import a local library
from mds_db import *

# Create an object of type mds_db
db = mds_db("dfs.db") 
db.Connect()
db.InsertFile('/hola/boo.txt', 20)
db.InsertFile('/opt/boo.txt', 30)
print(db.InsertFileName("Skibiddi"))
blockList = [('localhost', 4787, '296ba166-9222-11ee-904e-acde48001122'), ('localhost', 4939, '296bc682-9222-11ee-8ede-acde48001122')]
print(blockList)
print(db.AddBlockToInode('/hola/boo.txt', blockList))
db.Close() 
