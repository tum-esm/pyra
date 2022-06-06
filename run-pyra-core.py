import json
import os
import sys
from packages.core import main

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESS_STATE_FILE = os.path.join(PROJECT_DIR, "pyra-core-process-state.json")

# process is already running/has not been terminated correctly
if os.path.exists(PROCESS_STATE_FILE):
    sys.exit()

with open(PROCESS_STATE_FILE, "w") as f:
    json.dump({"pid": os.getpid()}, f)

try:
    main.run()
except:
    os.remove(PROCESS_STATE_FILE)
