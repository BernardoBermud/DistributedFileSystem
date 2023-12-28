This is an implementation of a simple, yet functional, distributed file system that can work locally 
as well as through a network of different computers. For the moment, this may contain an unreliable and 
insecure file server, hopefully someday the developer decides to pick this proyect up again to apply 
better security measures... 

This readme will be able to give you instructions on how to make it work and use it, as well as teach 
you how each part works.

#### Note:  Implementation done using Python 3 (3.8.3)

## Table of Contents
[Instructions](#instructions)
    [Set Up dfs](#setting-up-the-distributed-file-system)
    [Set Up copy Client](#copy-client)
    [Set Up ls Client](#ls-client)
    [Set Up rm Client](#copy-client)

[Program Logic](#distributed-file-system-programs-how-they-work)
    [Metadata Server Logic](#metadata-server-meta-datapy)
    [Data Server Logic](#data-server-data-nodepy)
    [ls Client logic](#ls-client-lspy)
    [copy Client logic](#copy-client-copypy)
    [rm Client logic](#rm-client-rmpy)


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
and from clients. While using the dfs, do not delete the files were data blocks are stored manually since it can cause 
problems trying to copy items from the dfs to your file system. If you want to reset the entire file system, 
you must remove "dfs.db" and repeat step 1, keep in mind that you still need to remove manually the files were 
data blocks are stored. 


## Copy client

1.  To copy a file to the distributed file system, use the following argument format.

    Input:  `python3 copy.py <source file> <server>:<port>:<dfs file path>`

    Server is the IP address were the metadata server is running, and port is it's port.
    dfs file path is were you write what that copied file will be named in the dfs.


2.  To copy a file from the distributed file system, use the following argument format.

    Input:  `python3 copy.py <server>:<# Abstracte file in the dfs that you want to copy and the destination
    file is where it will be copied to.

Disclaimer: Naming files in dfs using the ':' character will not work due to argument format.

## ls client

1.  To list the current files being stored in the distributed file system, use the following argument format:

    Input: `python3 ls.py <server>:<port, default=8000>`

    Server is the metadata server address and metadata port is the optional metadata 
    port if it was run in a different port other than the default port. The list should display the 
    file name along side it's attributes, in this case the size of the file.

## rm client

1.  To delete a file from the distributed file system, use the following argument format:

    Input: `python3 rm.py <server>:<port>:<dfs file path>`

    Server is the ip where the metadata server is running, and port it's the port that the metadata
    server is using. The data blocks that belonged to that file should be deleted as well as the file 
    not appearing anymore when you run the ls client.

# Distributed File System Programs (How They Work)

This distributed file system consists of  a metadata server, data servers, an ls client, and a copy client.
The servers and clients send and recieve commands and information from the packets library (Packet.py)
utilizing the socket library for communication.

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
This request commands are "get", "put", "reg", "list", "dblks". Based on the command sent by client, it chooses the process that needs to do. Uses functions from mds_db.py to retrieve and store information in database. 

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

## rm client (rm.py)

The rm client makes sure that all the information of the file stored in the dfs is deleted. The client handles
file deletion communicating with the metadata server and data nodes that stored originally the datablocks.

It sends a request to the metadata server to recieve the inode information. With this information, it's able to send
each datanode server the respective blockid they are in charge of and delete the file were the block was being stored.