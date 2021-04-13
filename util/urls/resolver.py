from typing import Callable

from util.http.request import HTTPRequest
from util.http.response import HTTPResponse
from util.views.static import static
from urls import url_patterns


class URLResolver:
  """
  - class for URL resolving process
  """
  
  def resolve(self, request: HTTPRequest) -> Callable[[HTTPRequest], HTTPResponse]:
    """
    - resolve URL
    - return coresponded view if matched pattern is
    - return static view if not
    """
    
    for url_pattern in url_patterns:
      match = url_pattern.match(request.path)
      if match:
          request.params.update(match.groupdict())
          return url_pattern.view
    
    return static