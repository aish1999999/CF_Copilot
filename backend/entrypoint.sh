#!/bin/bash

# Exit on error
set -e

# Check if database exists
if [ ! -f "/app/cf_copilot.db" ]; then
    echo "Database not found. Initializing..."

    # Extract PDF data
    echo "Extracting PDF data..."
    python scripts/extract_pdf_data.py

    # Seed database
    echo "Seeding database..."
    python scripts/seed_database.py

    echo "Database initialization complete!"
else
    echo "Database already exists. Skipping initialization."
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
