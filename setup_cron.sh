#to run: "chmod +x setup_cron.sh" THEN "./setup_cron.sh"
# This script sets up a cron job to run a Python script every 15 minutes.
# It assumes you have a Python virtual environment and a script to run.
# Make sure to replace the paths with your actual Python environment and script paths.

#!/bin/bash

# Load variables from .env
export $(grep -v '^#' .env | xargs)

# Verify that all required variables are set
if [[ -z "$PYTHON_EXEC" || -z "$SCRIPT_PATH" || -z "$LOG_PATH" ]]; then
  echo "ERROR: Required environment variables (PYTHON_EXEC, SCRIPT_PATH, LOG_PATH) not set."
  exit 1
fi

# Cron schedule - every 15 minutes
CRON_SCHEDULE="*/15 * * * *"

# Full cron command
CRON_CMD="$CRON_SCHEDULE $PYTHON_EXEC $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Add the cron command, avoiding duplicates
(crontab -l | grep -v -F "$SCRIPT_PATH"; echo "$CRON_CMD") | crontab -

echo "Cron job installed successfully."
