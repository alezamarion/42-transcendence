#!/bin/bash

# Find and remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +
find . -name "*.pyc" -delete