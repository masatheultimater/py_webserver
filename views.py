import urllib.parse
from datetime import datetime
from pprint import pformat

from util.http.cookie import Cookie
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
  
  context = {"request": request, "headers": pformat(request.headers), "body": request.body.decode("utf-8", "ignore")}
  body = render("show_request.html", context)
  
  return HTTPResponse(body=body)


def parameters(request: HTTPRequest) -> HTTPResponse:
  """
  - show POST parameters in HTTP request
  """
  
  # return 405 error 
  if request.method == "GET":
    body = b"<html><body><h1>405 Method Not Allowed!</h1></body></html>"
    
    return HTTPResponse(body=body, status_code=405)
    
  elif request.method == "POST":
    # decode the body & parse decoded query parameters(str)
    
    context = {"params": urllib.parse.parse_qs(request.body.decode())}
    body = render("parameters.html", context)
    
    return HTTPResponse(body=body)


def user_profile(request: HTTPRequest) -> HTTPResponse:
  """
  - return REST style user resource 
  """

  context = {"user_id": request.params["user_id"]}
  body = render("user_profile.html", context)
  
  return HTTPResponse(body=body)


def set_cookie(request: HTTPRequest) -> HTTPResponse:
  """
  - set cookie in response header
  """
  
  return HTTPResponse(cookies=[Cookie(name="username", value="MASA")])


def login(request: HTTPRequest) -> HTTPResponse:
  """
  - login to welcome page
  - if it's the first visit, show login page
  - otherwise, keep name from cookie & redirect to /welcome
  """

  if request.method == "GET":
    body = render("login.html", {})
    
    return HTTPResponse(body=body)
  
  elif request.method == "POST":
    # get username from input name in POST request body
    post_params = urllib.parse.parse_qs(request.body.decode())
    username = post_params["username"][0]
    email = post_params["email"][0]

    cookies = [
      Cookie(name="username", value=username, max_age=30),
      Cookie(name="email", value=email, max_age=30),
    ]
    
    return HTTPResponse(
      status_code=302,
      headers={"Location" : "/welcome"},
      cookies=cookies
    )


def welcome(request: HTTPRequest) -> HTTPResponse:
  """
  - show welcome page to identified user who has input user name in login page
  """
  
  # if not been loged in , redirect to /login
  if "username" not in request.cookies:
    return HTTPResponse(status_code=302, headers={"Location": "/login"})

  username = request.cookies["username"]
  email = request.cookies["email"]

  body = render("welcome.html", context={"username": username, "email": email})

  return HTTPResponse(body=body)