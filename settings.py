import os

# directory which has main script file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# directory which has static file to broadcast
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# directory which has template file
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

