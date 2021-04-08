import socket

class TCPServer:
  """
  class for TCP server
  """
  def serve(self):
    
    print("=== server start ===")
    
    try:
      # create socket
      server_socket = socket.socket()
      server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      # allocate socket to localhost:8080
      server_socket.bind(("localhost", 8080))
      server_socket.listen(10)

      # wait for request
      print("=== wait for client request")

      (client_socket, address) = server_socket.accept()

      print(f"=== connection to client has been completed, remote_address: {address} ===")
      
      # get data from client
      request = client_socket.recv(4096)

      # write down the data to file
      with open("server_recv.txt", "wb") as f:
        f.write(request)

      # terminate the connection
      client_socket.close()

    finally:
      print("=== stop server ===")
      
if __name__ == '__main__':
  server = TCPServer()   
  server.serve()

      
