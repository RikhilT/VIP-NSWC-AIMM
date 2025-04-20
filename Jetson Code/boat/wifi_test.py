import socket

# Create a new socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to an address and a port
host = socket.gethostname()
ip = socket.gethostbyname(host)
print(ip)
server_socket.bind(('10.42.0.1', 54321))

# Listen for incoming connections (the argument defines the max number of queued connections)
server_socket.listen(5)

print("Server is listening for connections...")

# Accept a connection
client_socket, addr = server_socket.accept()

print(f"Connection established with {addr}")

client_socket.send("Please Work".encode())
client_socket.close()