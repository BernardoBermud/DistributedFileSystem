Name:   Bernardo A. Bermúdez Noriega
Stu#:   801-19-6346
Clss:   CCOM4017
Proj:   Assignment 04: Distributed File systems
Date:   December 7, 2023

Version Information:
Code -> Python 3.8.3

Instructions - Setting Up the Distributed File system

1.  Create the database for the dfs running the "createdb.py" file, you should see a file named 
    "dfs.db" afterwards.


2.  Run the metadata server program using the following argument format:

    Input:  python3 meta-data.py <port, default=8000>

    If port is specified, the metadata server will run on port 8000 by default


3.  Run the datanode server program using the following argument format:

    Input:  python3 data-node.py <server address> <port> <data path> <metadata port,default=8000>

    Server address is the metadata server address, port is the datanode port number, 
    data path is a path to a directory to store the data blocks, and metadata port is 
    the optional metadata port if it was run in a different port other than the default port.
    You can run multiple datanode servers as long as they all have different port numbers,
    keep in mind that, once the metadata has registered them, they must be running 
    for the dfs to work correctly. If you want to use a different amout of datanodes, you must
    remove the database "dfs.db" and repeat step 1.

Given there conditions the distributed file system should be ready to recieve and send commands to
and from clients


Instructions - Copy client

1.  To copy a file to the distributed file system, use the following argument format.

    Input:  python3 copy.py <source file> <server>:<port>:<dfs file path>

    Server is the IP address were the metadata server is running, and port is it's port.
    dfs file path is were you write what that copied file will be named in the dfs.


2.  To copy a file from the distributed file system, use the following argument format.

    Input:  python3 copy.py <server>:<port>:<dfs file path> <destination file>

    Server is the IP address were the metadata server is running, and port is it's port.
    The dfs file path is the name of the file in the dfs that you want to copy and the destination
    file is where it will be copied to.


Instructions - ls client

1.  To list the current files being stored in the distributed file system, use the following argument format:

    Input: python3 ls.py <server>:<port, default=8000>

    server is the metadata server address and metadata port is the optional metadata 
    port if it was run in a different port other than the default port. The list should display the 
    file name along side it's attributes, in this case the size of the file.



