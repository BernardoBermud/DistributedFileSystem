Name:   Bernardo A. Bermúdez Noriega
Stu#:   801-19-6346
Clss:   CCOM4017
Proj:   Assignment 04: Distributed File systems
Date:   December 7, 2023

Verbal Colaborations: Sergio D. Rodriguez de Jesús.

# Instructions 

## Setting Up the Distributed File system

1.  Create the database for the dfs running the "createdb.py" file, you should see a file named 
    "dfs.db" afterwards.


2.  Run the metadata server program using the following argument format:

    Input:  `python3 meta-data.py <port, default=8000>`

    If port is specified, the metadata server will run on port 8000 by default


3.  Run the datanode server program using the following argument format:

    Input:  `python3 data-node.py <server address> <port> <data path> <metadata port,default=8000>`

    Server address is the metadata server address, port is the datanode port number, 
    data path is a path to a directory to store the data blocks, and metadata port is 
    the optional metadata port if it was run in a different port other than the default port.
    You can run multiple datanode servers as long as they all have different port numbers,
    keep in mind that, once the metadata has registered them, they must be running 
    for the dfs to work correctly. If you want to use a different amout of datanodes, you must
    remove the database "dfs.db" and repeat step 1.

Given these conditions, the distributed file system should be ready to recieve and send commands to
and from clients


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


## ls client

1.  To list the current files being stored in the distributed file system, use the following argument format:

    Input: `python3 ls.py <server>:<port, default=8000>`

    server is the metadata server address and metadata port is the optional metadata 
    port if it was run in a different port other than the default port. The list should display the 
    file name along side it's attributes, in this case the size of the file.


# Distributed File System Programs

This distributed file system consists of a metadata server, data servers, an ls client, and a copy client.
The servers and clients send and recieve commands and information utilizing the packets library to encode 
and decode information with json.

## Metadata Server (meta-data.py)

The metadata server keeps track of all file information, including the file name, size, and location 
of data blocks and stores that information in the data base.

It provides the following key functions:

-   Registers new data nodes as they come online ("reg")
-   Stores files and attributes (name, size) in database when new files are added ("put")
-   Returns list of available data nodes when client requests to write a file ("put")
-   Returns a list of files and their attributes when the ls client requests it ("list")
-   Returns a list of blocks containing datanode ip, datanode port and id where memory is stored (block id)
    when client requests to read a file ("get")
-   Stores inode when client finishes writing a file ("dblks")

The metadata server runs on a designated port and listens for requests from datanodes and clients. 
This request commands are "get", "put", "reg", "list", "dblks". Based on the command sent by client, it chooses 
the process that needs to do.

## Data Server (data-node.py)

Data servers store the actual file data blocks. 

They provide the following key functions:

-   Register themselves with the metadata server on startup.("reg")
-   Receive and store data blocks from clients, assigning a unique ID to each block and sending
    it back to client.("put")
-   Retrieve and return data blocks when requested by clients utilizing the unique ID sent by the
    client utilizing the block info (data IP, data port, bock id). ("get")

Data servers run on assigned ports and listen for block read/write requests. 
The request commands are "get", "put". Based on the command sent by copy client, it chooses the process 
that needs to do. The process of recieving and transfering of memory blocks between data node and client 
is done sending them in chunks of 4KB at a time in order to avoid loosing bits. In this implementation, 
they store the blocks of data as files within the users file system in the directory they've chosen 
(`<path>`). Multiple data servers can run per machine on different ports. 

## ls Client (ls.py)

The ls client lists all files stored in the DFS along with their attributes.

It sends a request "list" to the metadata server, which returns the file list stored in the database. 
The ls client then prints this list.

## Copy Client (copy.py)

The copy client copies files to and from the DFS. The client handles file transfer coordination 
with both the metadata and data servers.

Key functions:

-   Write "put": Sends file name/size to metadata server, receives datanode list, divides file into 
    memory blocks by dividing the file size with the amount of datanodes recieved in the list. Send 
    to the datanode the "put" request and the size of the block that will be sent and be ready to recieve 
    the memory block by chunks. Sends a data block to each data node in the list. After datanode stored 
    the block, it returns the unique ID that will be stored as the block info by the copy client. Sends
    list of blocks to metadata to store in database.

-   Read "get": Requests file inode with data blocks from metadata server "get", it divides the file size by the amount 
    of datanodes to know the size of blocks that will be recieved. Retrieves blocks from data nodes 
    as it reassembles file as it retrieves the blocks from data nodes.

The process of recieving and transfering of memory blocks between data node and copy client is done 
sending them in chunks of 4KB at a time in order to avoid loosing bits.