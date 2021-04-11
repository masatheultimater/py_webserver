import os
import textwrap
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple, Optional


class WorkerThread(Thread):
  """
  class for worker thread
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
  
  def __init__(self, client_socket: socket, address: Tuple[str, int]):
    super().__init__()
    
    self.client_socket = client_socket
    self.client_address = address

  def run(self) -> None:
    """
    - receive socket which has completed to connecte with client
    - proceed request and send response
    """

    print(f"=== Worker: start the interaction with client, remote_address: {self.client_address} ===")
    
    try:
      # get data from client request
      request = self.client_socket.recv(4096)

      # write the data from request down to file
      with open("server_recv.txt", "wb") as f:
        f.write(request)
      
      # parse the HTTP request
      method, path, http_version, request_header, request_body = self.parse_http_request(request)

      # give anotations to the variables of request
      response_body: bytes
      content_type: Optional[str]
      response_line: str

      # create HTML which shows now date if request path is /now
      if path == "/now":
        html = f"""\
          <html>
          <body>
            <h1>Now: {datetime.now()}</h1>
          </body>
          </html>
        """
        response_body = textwrap.dedent(html).encode()
        
        # designate Content-Type
        content_type = "text/html"

        # create response line
        response_line = "HTTP/1.1 200 OK\r\n"
      
      # create static HTML if the path is not \now
      else:
        try:
          # create response body from static file
          response_body = self.get_static_file_content(path)
          
          # desinate Content-Type
          content_type = None
        
          # create response line
          response_line = "HTTP/1.1 200 OK\r\n"

        # TODO: distinguish more detailed sub class exception(e.g. FileNotFound, ISADirectory..)
        except OSError:
          # return 404 error in case of file not found
          traceback.print_exc()

          response_body = b"<html><body><h1>404 Not Found!</h1></body></html>"
          content_type = "text/html"
          response_line = "HTTP/1.1 404 Not Found\r\n"
      
      # create response header
      response_header = self.build_response_header(path, response_body, content_type)
      
      # create whole response with joining headers and body
      response = (response_line + response_header + "\r\n").encode() + response_body
      
      # send response to client
      self.client_socket.send(response)
    
    except Exception:
      # case if exception thrown during processing requests
      # output error logs in console, and keep processing
      print("=== Worker: Error occured in processing request ===")
      traceback.print_exc()
    
    finally:
      # terminate the connection(whenver exception has occured or not)
      print(f"=== Worker: terminate the interaction with client, remote_address: {self.client_address} ===")
      self.client_socket.close()
  
  def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
    """
    - split/parse the HTTP request into
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
  
  def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str]) -> str:
    """
    - build response header
    """
    
    # get Content-Type from request data
    ## if the Content-Type is not designated
    if content_type is None:
      # get extension from path
      if "." in path:
        ext = path.rsplit(".", maxsplit=1)[-1]
      else:
        ext =""
      # get MIME-Type from ext
      # give it octet-stream if the ext is not corresponded
      content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
      
    

    
    # create response header
    response_header = ""
    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response_header += "Host: NinjaServer/0.1\r\n"
    response_header += f"Content-Length: {len(response_body)}\r\n"
    response_header += "Connection: Close\r\n"
    response_header += f"Content-type: {content_type}\r\n"
    
    return response_header
