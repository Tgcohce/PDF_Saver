#!/bin/bash

# Path to the Python script
PYTHON_SCRIPT="upload_to_sheets.py"

# Run the Python script
echo "Running Python script to upload data to Google Sheets..."
python3 "$PYTHON_SCRIPT"

# Check if the Python script executed successfully
if [ $? -eq 0 ]; then
    echo "Python script executed successfully."
else
    echo "Python script failed."
fi
