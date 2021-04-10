import socket
from workerthread import WorkerThread


class WebServer:
  """
  class for Web server
  """

  def serve(self):
    """
    - start server
    """
    print("=== Server: server start ===")
    
    try:
      # create socket
      server_socket = self.create_server_socket()

      # looped wait for request
      while True:
        # wait for request and create connection if request exits
        print("=== Server: wait for request ===")
        (client_socket, address) = server_socket.accept()
        print(f"=== Server: complete connection to client, remote_address: {address} ===")

        # create thread to proceed client request
        thread = WorkerThread(client_socket, address)
        # run thread
        thread.start()

    finally:
      print("=== Server: stop server ===")

  def create_server_socket(self) -> socket:
    """
    - create server_socket to receive TCP/HTTP request
    """

    # create socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # allocate socket to localhost:8080
    server_socket.bind(("localhost", 8080))
    server_socket.listen(10)
    return server_socket
    
 
if __name__ == '__main__':
  server = WebServer()   
  server.serve()

      
