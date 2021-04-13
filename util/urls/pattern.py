import re
from re import Match
from typing import Callable, Optional

from util.http.request import HTTPRequest
from util.http.response import HTTPResponse

class URLPattern:
  """
  - class for URL match process 
  """
  
  pattern: str
  view: Callable[[HTTPRequest], HTTPResponse]
  
  def __init__(self, pattern: str, view: Callable[[HTTPRequest], HTTPResponse]):
    self.pattern = pattern
    self.view = view
    
  def match(self, path: str) -> Optional[Match]:
    """
    - judge if the path matches with URL pattern or not
    - return Match object if matched
    """
    # parse URL to regular expression
    # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
    pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)
    return re.match(pattern, path)