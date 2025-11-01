#!/bin/bash
# Helper script to run generate_logs.py in the virtual environment

cd /home/ademm/saas-monitoring-platform

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Installing Faker..."
    source venv/bin/activate
    pip install Faker
else
    source venv/bin/activate
fi

# Run the script
echo "Running generate_logs.py..."
python generate_logs.py

# Deactivate when done
deactivate

echo ""
echo "Done! Files created in uploads/ directory."
