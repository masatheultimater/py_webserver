def render(template_path: str, context: dict):
  """
  - read template HTML file & format variables in it
  """
  
  with open(template_path) as f:
    template = f.read()

  return template.format(**context)