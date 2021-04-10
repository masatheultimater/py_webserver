import os
import socket
from datetime import datetime


class WebServer:
  """
  class for Web server
  """
  
  # main script directory (py_webserver/web)
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  # static file directory (py_webserver/static)
  STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, "../static"))
  
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
      
      # parse the whole request to line, header, body
      request_line, remain = request.split(b"\r\n", maxsplit=1)
      request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

      # process request line
      ## parse whole line
      method, path, http_version = request_line.decode().split(" ")
      ## delete front / and make it relative path
      relative_path = path.lstrip("/")
      ## get the file path
      static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
      
      # create response body with static file
      with open(static_file_path, "rb") as f:
        response_body = f.read()
      
      # create response line
      response_line = "HTTP/1.1 200 OK\r\n"

      # create response header
      response_header = ""
      response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
      response_header += "Host: NinjaServer/0.1\r\n"
      response_header += f"Content-Length: {len(response_body)}\r\n"
      response_header += "Connection: Close\r\n"
      response_header += "Content-type: text/html\r\n"

      # create whole response with joining headers and body
      response = (response_line + response_header + "\r\n").encode() + response_body
      
      # send response to client
      client_socket.send(response)
      
      # terminate the connection
      client_socket.close()

    finally:
      print("=== stop server ===")
      
if __name__ == '__main__':
  server = WebServer()   
  server.serve()

      
