import subprocess
import time
import signal
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths from .env
PYTHON_EXEC = os.getenv("PYTHON_EXEC")
SCRIPT_PATH = os.getenv("SCRIPT_PATH")

if not PYTHON_EXEC or not SCRIPT_PATH:
    print("ERROR: PYTHON_EXEC and SCRIPT_PATH must be set in your .env file.")
    sys.exit(1)

# Interval in seconds (aka 900==15 minutes)
INTERVAL = 90  

COMMAND = [PYTHON_EXEC, SCRIPT_PATH]

def signal_handler(sig, frame):
    print('\nScript stopped manually.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("Starting periodic execution... (press Ctrl+C to stop)")

while True:
    subprocess.run(COMMAND)
    print(f"Waiting {INTERVAL} seconds...")
    time.sleep(INTERVAL)
