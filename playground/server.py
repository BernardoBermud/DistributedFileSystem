import socket
import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        # Send back the same data
        self.request.sendall(data)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    host = "localhost"  # Use 'localhost' to only allow connections from the same machine
    port = int(sys.argv[1])

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print(f"Server listening on {host}:{port}")
    server.serve_forever()
