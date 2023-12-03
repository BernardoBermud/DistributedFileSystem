import socket
import sys

if len(sys.argv) != 4:
    print("Usage: python otherfile.py <server_address> <otherfile_port> <server_port>")
    sys.exit(1)

server_address = sys.argv[1]
otherfile_port = int(sys.argv[2])
server_port = int(sys.argv[3])

# Connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((server_address, server_port))

    # Send data to the server
    message = "Hello, server! This is the other file."
    s.sendall(message.encode())

    # Receive the response from the server
    data = s.recv(1024).decode()
    print(f"Server response: {data}")