import re
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple

from util.http.request import HTTPRequest
from util.http.response import HTTPResponse
from util.urls.resolver import URLResolver


class Worker(Thread):
  """
  class for worker thread
  """

  # dynamic choice of MIME Type & file extention
  MIME_TYPES = {
    "html": "text/html; charset=UTF-8",
    "css": "text/css",
    "png": "image/png",
    "jpg": "image/jpg",
    "gif": "image/gif",
  }
  
  # TODO: correspond to more status_codes(100s, 300s, 500s...)
  # correspondence between status_code & status_line
  STATUS_LINES = {
    200: "200 OK",
    302: "302 Found",
    404: "404 Not Found",
    405: "Method Not Allowed",
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
      request_bytes = self.client_socket.recv(4096)

      # write the data from request down to file
      with open("server_recv.txt", "wb") as f:
        f.write(request_bytes)
      
      # parse the HTTP request
      request = self.parse_http_request(request_bytes)

      # URL resolve
      view = URLResolver().resolve(request)
      
      # create response from view 
      response = view(request)
      
      # parse response body str -> bytes
      if isinstance(response.body, str):
        response.body = response.body.encode()
      
      # create response line
      response_line = self.build_response_line(response)
      
      # create response header
      response_header = self.build_response_header(response, request)

      # create whole response with joining headers and body
      response_bytes = (response_line + response_header + "\r\n").encode() + response.body
      
      # send response to client
      self.client_socket.send(response_bytes)
    
    except Exception:
      # case if exception thrown during processing requests
      # output error logs in console, and keep processing
      print("=== Worker: Error occured in processing request ===")
      traceback.print_exc()
    
    finally:
      # terminate the connection(whenver exception has occured or not)
      print(f"=== Worker: terminate the interaction with client, remote_address: {self.client_address} ===")
      self.client_socket.close()
  
  def parse_http_request(self, request: bytes) -> HTTPRequest:
    """
    - split/parse the HTTP request into HTTPRequest dataclass
    """
    
    # parse the whole request into line, header, body
    request_line, remain = request.split(b"\r\n", maxsplit=1)
    request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

    # process request line
    ## parse line into String
    method, path, http_version = request_line.decode().split(" ")
    
    ## parse request header into dictionary
    headers = {}
    for header_row in request_header.decode().split("\r\n"):
      key, value = re.split(r": *", header_row, maxsplit=1)
      headers[key] = value
    
    return HTTPRequest(
      method=method,
      path=path,
      http_version=http_version,
      headers=headers,
      body=request_body
    )
   
  def build_response_line(self, response: HTTPResponse) -> str:
    """
    - build response line
    """
    
    status_line = self.STATUS_LINES[response.status_code]
    return f"HTTP/1.1 {status_line}"
  
  def build_response_header(self, response: HTTPResponse, request: HTTPRequest) -> str:
    """
    - build response header
    """
    
    # get Content-Type from request data
    ## if the Content-Type is not designated
    if response.content_type is None:
      # get extension from path
      if "." in request.path:
        ext = request.path.rsplit(".", maxsplit=1)[-1]
        # get MIME-Type from ext
        # give it octet-stream if the ext is not corresponded
        response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
      else:
        # treat it as html if no extension
        response.content_type = "text/html; charset=UTF-8"

      
    # create response header
    response_header = ""
    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response_header += "Host: NinjaServer/0.1\r\n"
    response_header += f"Content-Length: {len(response.body)}\r\n"
    response_header += "Connection: Close\r\n"
    response_header += f"Content-type: {response.content_type}\r\n"
    
    # add multiple cookie headers
    for cookie_name, cookie_value in response.cookies.items():
      response_header += f"Set-Cookie: {cookie_name}={cookie_value}\r\n"
    
    # add headers attributes in response object
    for header_name, header_value in response.headers.items():
      response_header += f"{header_name}: {header_value}\r\n"
    
    return response_header

