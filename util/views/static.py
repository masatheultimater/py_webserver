import os
import traceback

import settings
from util.http.request import HTTPRequest
from util.http.response import HTTPResponse


def static(request: HTTPRequest) -> HTTPResponse:
  """
  - get response from static file
  """
  
  try:
    static_root = getattr(settings, "STATIC_ROOT")

    # delete front / and make it relative path
    relative_path = request.path.lstrip("/")
    # get the file path
    static_file_path = os.path.join(static_root, relative_path)
    
    with open(static_file_path, "rb") as f:
      response_body = f.read()

    content_type = None
    
    return HTTPResponse(
      body=response_body,
      content_type=content_type,
      status_code=200
    )

  # TODO: distinguish more detailed sub class exception(e.g. FileNotFound, ISADirectory..)
  except OSError:
    # return 404 error in case of file not found
    traceback.print_exc()

    response_body = b"<html><body><h1>404 Not Found!</h1></body></html>"
    content_type = "text/html;"
    
    return HTTPResponse(
      body=response_body,
      content_type=content_type,
      status_code=404
    )