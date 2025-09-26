#!/bin/bash

# Script to start AI Learning Hub application in development mode
echo "Starting AI Learning Hub application in DEVELOPMENT mode on port 5051..."
echo "Access the application at: http://localhost:5051"
echo "Debug mode: ENABLED"

# Make the Python script executable
chmod +x ai_learning_hub_dev.py

# Run the Python script
python3 ai_learning_hub_dev.py