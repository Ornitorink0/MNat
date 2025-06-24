#!/bin/bash

if [ "$1" = "clean" ]; then
    echo "Cleaning virtual environment..."
    rm -rf ./venv
    echo "Cleaned virtual environment."
else
    echo "Creating virtual environment..."
    python3 -m venv ./venv
    echo "Activating virtual environment..."
    source ./venv/bin/activate
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    echo "Starting application..."
    sudo ./venv/bin/python src/app.py
fi

