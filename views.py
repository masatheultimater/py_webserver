import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat

from util.http.request import HTTPRequest
from util.http.response import HTTPResponse
from util.template.renderer import render


def now(request: HTTPRequest) -> HTTPResponse:
  """
  - create dynamic HTML that shows now date
  """

  context = {"now": datetime.now()}
  body = render("now.html", context)
  
  return HTTPResponse(body=body)


def show_request(request: HTTPRequest) -> HTTPResponse:
  """
  - create dynamic HTML that shows contents of HTTP request
  """
 
  html = f"""\
    <html>
    <body>
      <h1>Request Line:</h1>
      <p>
        {request.method} {request.path} {request.http_version}
      </p>
      <h1>Headers:</h1>
      <pre>{pformat(request.header)}</pre>
      <h1>Body:</h1>
      <pre>{request.body.decode("utf-8", "ignore")}</pre>

    <body>
    <html>
  """ 
  
  body = textwrap.dedent(html).encode()

  # designate Content-Type
  content_type = "text/html; charset=UTF-8"
  
  return HTTPResponse(body=body, content_type=content_type, status_code=200)


def parameters(request: HTTPRequest) -> HTTPResponse:
  """
  - show POST parameters in HTTP request
  """
  
  # return 405 error 
  if request.method == "GET":
    body = b"<html><body><h1>405 Method Not Allowed!</h1></body></html>"
    content_type = "text/html; charset=UTF-8"
    status_code = 405

  elif request.method == "POST":
    # decode the body & parse decoded query parameters(str)
    post_params = urllib.parse.parse_qs(request.body.decode())
    html = f"""\
      <html>
      <body>
        <h1>Parameters:</h1>
        <pre>{pformat(post_params)}</pre>
      <body>
      <html>
    """
    
    body = textwrap.dedent(html).encode()

    # designate Content-Type
    content_type = "text/html; charset=UTF-8"

    status_code = 200

  return HTTPResponse(body=body, content_type=content_type, status_code=status_code)


def user_profile(request: HTTPRequest) -> HTTPResponse:
  """
  - return REST style user resource 
  """
  user_id = request.params["user_id"]
  html = f"""\
    <html>
    <body>
      <h1>Profile</h1>
      <p>ID: {user_id}</p>
    </body>
    </html>
  """
  body = textwrap.dedent(html).encode()
  content_type = "text/html; charset=UTF-8"
  status_code = 200
  
  return HTTPResponse(
    body=body,
    content_type=content_type,
    status_code=status_code
  )