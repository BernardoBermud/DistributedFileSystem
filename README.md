#### Name:   Bernardo A. Bermúdez Noriega
#### Stu#:   801-19-6346
#### Clss:   CCOM4017
#### Proj:   Assignment 04: Distributed File systems
#### Date:   December 7, 2023
#### Verbal Colaborations: Sergio D. Rodriguez de Jesús and Yadriel O. Camis Bonilla

## Note:  Implementation done using Python 3 (3.8.3)

# Instructions 

## Setting Up the Distributed File system

1.  Create the database for the dfs running the "createdb.py" file, you should see a file named 
    "dfs.db" afterwards.


2.  Run the metadata server program using the following argument format:

    Input:  `python3 meta-data.py <port, default=8000>`

    If port is not specified, the metadata server will run on port 8000 by default


3.  Run the datanode server program using the following argument format:

    Input:  `python3 data-node.py <server address> <port> <data path> <metadata port,default=8000>`

    Server address is the metadata server address, port is the datanode port number, 
    data path is a path to a directory to store the data blocks, and metadata port is 
    the optional metadata port if it was run in a different port other than the default port.
    You can run multiple datanode servers as long as they all have different port numbers,
    keep in mind that, once the metadata has registered them, they must be running 
    for the dfs to work correctly. If you want to use a different amout of datanodes, you must
    remove the database "dfs.db" and repeat step 1. Make sure that the datanode always runs in the 
    same data path, otherwise this may cause issues when retrieving files in the dfs.

Given these conditions, the distributed file system should be ready to recieve and send commands to
and from clients. If you want to delete the files in the dfs, you must remove "dfs.db" and repeat
step 1, keep in mind that you still need to remove manually the files were data blocks are stored.


## Copy client

1.  To copy a file to the distributed file system, use the following argument format.

    Input:  `python3 copy.py <source file> <server>:<port>:<dfs file path>`

    Server is the IP address were the metadata server is running, and port is it's port.
    dfs file path is were you write what that copied file will be named in the dfs.


2.  To copy a file from the distributed file system, use the following argument format.

    Input:  `python3 copy.py <server>:<port>:<dfs file path> <destination file>`

    Server is the IP address were the metadata server is running, and port is it's port.
    The dfs file path is the name of the file in the dfs that you want to copy and the destination
    file is where it will be copied to.

Disclaimer: Naming files in dfs using the ':' character will not work due to argument format.

## ls client

1.  To list the current files being stored in the distributed file system, use the following argument format:

    Input: `python3 ls.py <server>:<port, default=8000>`

    server is the metadata server address and metadata port is the optional metadata 
    port if it was run in a different port other than the default port. The list should display the 
    file name along side it's attributes, in this case the size of the file.


# Distributed File System Programs

This distributed file system consists of a metadata server, data servers, an ls client, and a copy client.
The servers and clients send and recieve commands and information from the packets library utilizing the socket
library for communication.

## Metadata Server (meta-data.py)

The metadata server keeps track of all file information, including the file name, size, and location 
of data blocks and stores that information in the data base.

It provides the following key functions:

-   Registers new data nodes as they come online.
-   Stores files and attributes (name, size) when new files are added.
-   Returns list of available data nodes when client requests to write a file.
-   Returns a list of files and their attributes when the ls client requests it.
-   Returns a list of blocks containing datanode ip, datanode port and id where memory is stored (block id)
    when copy client requests to read a file.
-   Stores inode when client finishes writing a file.

The metadata server runs on a designated port and listens for requests from datanodes and clients. 
This request commands are "get", "put", "reg", "list", "dblks". Based on the command sent by client, it chooses the process that needs to do. Uses functions from mds_db.py to retrieve and store information
in database. 

## Data Server (data-node.py)

Data servers store the actual file data blocks. 

They provide the following key functions:

-   Register themselves with the metadata server on startup.
-   Receive and store data blocks from copy client, assigning a unique ID to each block and sending
    it back to copy client.
-   Retrieve and return data blocks when requested by copy client utilizing the unique ID sent by the
    copy client using the block info (data IP, data port, bock id).

Data servers run on assigned ports and listen for block read/write requests. 
The request commands are "get", "put". Based on the command sent by copy client, it chooses between 
send and recieve. The process of recieving and sending memory blocks between data node and copy client,  
is done sending them in chunks of 4KB at a time in order to avoid loosing bits. In this implementation, 
the blocks of data are stored as files within the users file system in the directory they've chosen 
(`<path>`). Multiple data servers can run per machine on different ports. 

## ls Client (ls.py)

The ls client lists all files stored in the DFS along with their attributes.

It sends a request "list" to the metadata server, which returns the file list. 
The ls client then prints this list.

## Copy Client (copy.py)

The copy client copies files to and from the DFS. The client handles file transfer coordination 
with both the metadata and data servers.

Key functions:

-   Write: Sends file name/size to metadata server, receives datanode list, divides file into 
    memory blocks using the amount of datanodes recieved in the list. Send 
    to the datanode the request and the size of the block that will be sent so it's ready to recieve 
    the memory block. Sends a data block to each data node in the list. After datanode stored the 
    block, it returns the unique ID that will be stored as the block info by the copy client. copy client
    finishes by sending list of blocks so metadata server stores it.

-   Read: Requests file inode with data blocks from metadata server, it divides the file size by the amount 
    of datanodes to know the size of blocks that will be recieved. Retrieves blocks from data nodes 
    as it reassembles file as it retrieves the blocks from data nodes.

The process of recieving and transfering of memory blocks between data node and copy client is done 
sending them in chunks of 4KB at a time in order to avoid loosing bits.