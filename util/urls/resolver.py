

from typing import Callable, Optional
from util.http.request import HTTPRequest
from util.http.response import HTTPResponse
from urls import url_patterns


class URLResolver:
  """
  - class for URL resolving process
  """
  
  def resolve(self, request: HTTPRequest) -> Optional[Callable[[HTTPRequest], HTTPResponse]]:
    """
    - resolve URL
    - return coresponded view if matched pattern is
    """
    
    for url_pattern in url_patterns:
      match = url_pattern.match(request.path)
      if match:
          request.params.update(match.groupdict())
          return url_pattern.view
    
    return None