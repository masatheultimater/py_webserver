import os
import re
import traceback
from datetime import datetime
from re import Match
from socket import socket
from threading import Thread
from typing import Optional, Tuple

import settings
from util.http.request import HTTPRequest
from util.http.response import HTTPResponse
from web.urls import URL_VIEW


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

      # create response from view 
      for url_pattern, view in URL_VIEW.items():
        match = self.url_match(url_pattern, request.path)
        if match:
          request.params.update(match.groupdict())
          response = view(request)
          break
        
      # create static HTML if the path is not \now
      else:
        try:
          # create response body from static file
          response_body = self.get_static_file_content(request.path)
          
          # desinate Content-Type
          content_type = None
        
          # create response 
          response = HTTPResponse(body=response_body, content_type=content_type, status_code=200)
      
        # TODO: distinguish more detailed sub class exception(e.g. FileNotFound, ISADirectory..)
        except OSError:
          # return 404 error in case of file not found
          traceback.print_exc()

          response_body = b"<html><body><h1>404 Not Found!</h1></body></html>"
          content_type = "text/html;"
          response = HTTPResponse(
            body=response_body,
            content_type=content_type,
            status_code=404
          )
      
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

  def get_static_file_content(self, path: str) -> bytes:
    """
    - get static file contents from request path
    """
    
    default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
    static_root = getattr(settings, "STATIC_ROOT", default_static_root)

    # delete front / and make it relative path
    relative_path = path.lstrip("/")
    # get the file path
    static_file_path = os.path.join(static_root, relative_path)
    
    with open(static_file_path, "rb") as f:
      return f.read()
  
  
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
      else:
        ext =""
      # get MIME-Type from ext
      # give it octet-stream if the ext is not corresponded
      response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
      
    # create response header
    response_header = ""
    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response_header += "Host: NinjaServer/0.1\r\n"
    response_header += f"Content-Length: {len(response.body)}\r\n"
    response_header += "Connection: Close\r\n"
    response_header += f"Content-type: {response.content_type}\r\n"
    
    return response_header

  def url_match(self, url_pattern: str, path: str) -> Optional[Match]:
    # parse URL to regular expression
    # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
    re_pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", url_pattern)
    return re.match(re_pattern, path)
