import os
import socket
import traceback
from datetime import datetime
from typing import Tuple


class WebServer:
  """
  class for Web server
  """
  
  # main script directory (py_webserver/web)
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  # static file directory (py_webserver/static)
  STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, "../static"))
  
  # dynamic choice of MIME Type & file extention
  MIME_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "png": "image/png",
    "jpg": "image/jpg",
    "gif": "image/gif",
  }
  
  def serve(self):
    
    print("=== server start ===")
    
    try:
      # create socket
      server_socket = self.create_server_socket()

      # looped wait for request
      while True:
        # wait for request and create connection if request exits
        print("=== wait for request ===")
        (client_socket, address) = server_socket.accept()
        print(f"=== complete connection to client, remote_address: {address} ===")

        try:
          # interact with client, and proceed the request
          self.handle_client(client_socket)
          
        except Exception:
          # case if exception thrown during processing requests
          # output error logs in console, and keep processing
          print("=== Error occured in processing request ===")
          traceback.print_exc()

        finally: 
          # terminate the connection(whenver exception has occured or not)
          client_socket.close()

    finally:
      print("=== stop server ===")

  def create_server_socket(self) -> socket:
    """
    create server_socket to receive TCP/HTTP request
    """

    # create socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # allocate socket to localhost:8080
    server_socket.bind(("localhost", 8080))
    server_socket.listen(10)
    return server_socket
    
  def handle_client(self, client_socket: socket) -> None:
    """
    - receive socket which has completed to connecte with client
    - proceed request and send response
    """

    # get data from client request
    request = client_socket.recv(4096)

    # write the data from request down to file
    with open("server_recv.txt", "wb") as f:
      f.write(request)
    
    # parse the HTTP request
    method, path, http_version, request_header, request_body = self.parse_http_request(request)

    # create response body with static file
    try:
      # create response body from static file
      response_body = self.get_static_file_content(path)
    
      # create response line
      response_line = "HTTP/1.1 200 OK\r\n"

    # TODO: distinguish more detailed sub class exception(e.g. FileNotFound, ISADirectory..)
    except OSError:
      # case of file not found
      response_body = b"<html><body><h1>404 Not Found!</h1></body></html>"
      response_line = "HTTP/1.1 404 Not Found\r\n"
    
    # create response header
    response_header = self.build_response_header(path, response_body)
    
    # create whole response with joining headers and body
    response = (response_line + response_header + "\r\n").encode() + response_body
    
    # send response to client
    client_socket.send(response)

  def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
    """
    split/parse the HTTP request into
    1. method: str
    2. path: str
    3. http_version: str
    4. request_header: bytes
    5. request_body: bytes
    """
    # parse the whole request into line, header, body
    request_line, remain = request.split(b"\r\n", maxsplit=1)
    request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

    # process request line
    ## parse line into String
    method, path, http_version = request_line.decode().split(" ")
    
    return method, path, http_version, request_header, request_body

  def get_static_file_content(self, path: str) -> bytes:
    """
    - get static file contents from request path
    """
    # delete front / and make it relative path
    relative_path = path.lstrip("/")
    # get the file path
    static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
    
    with open(static_file_path, "rb") as f:
      return f.read()
  
  def build_response_header(self, path: str, response_body: bytes) -> str:
    """
    - build response header
    """
    # get Content-Type from request data
    ## get extention from path
    if "." in path:
      ext = path.rsplit(".", maxsplit=1)[-1]
    else:
      ext =""
    
    ## get MIME-Type from ext
    ## give it octet-stream if the ext is not corresponded
    content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
    
    # create response header
    response_header = ""
    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response_header += "Host: NinjaServer/0.1\r\n"
    response_header += f"Content-Length: {len(response_body)}\r\n"
    response_header += "Connection: Close\r\n"
    response_header += f"Content-type: {content_type}\r\n"
    
    return response_header

 
if __name__ == '__main__':
  server = WebServer()   
  server.serve()

      
