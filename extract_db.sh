#!/bin/bash

# Script to extract SQLite database from Arduino UNO Q Docker container
# Run this on your Debian environment on the UNO Q

echo "=== Arduino UNO Q Database Extractor ==="
echo ""

# Find the container running your brick
echo "Looking for running Docker containers..."
CONTAINER_ID=$(docker ps --filter "ancestor=*sqlstore*" --format "{{.ID}}" | head -n 1)

# If not found, try finding any container with your app
if [ -z "$CONTAINER_ID" ]; then
    echo "Searching for containers with database.db..."
    CONTAINER_ID=$(docker ps -q | head -n 1)
fi

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No running containers found!"
    echo ""
    echo "Available containers:"
    docker ps -a
    exit 1
fi

echo "✓ Found container: $CONTAINER_ID"
echo ""

# List files in container to find database location
echo "Searching for database.db in container..."
DB_PATH=$(docker exec $CONTAINER_ID find / -name "database.db" 2>/dev/null | head -n 1)

if [ -z "$DB_PATH" ]; then
    echo "❌ database.db not found in container"
    echo ""
    echo "Common locations to check:"
    docker exec $CONTAINER_ID ls -la /app/ 2>/dev/null
    docker exec $CONTAINER_ID ls -la /data/ 2>/dev/null
    docker exec $CONTAINER_ID ls -la /tmp/ 2>/dev/null
    exit 1
fi

echo "✓ Found database at: $DB_PATH"
echo ""

# Create output directory
OUTPUT_DIR="$HOME/arduino_data"
mkdir -p "$OUTPUT_DIR"

# Copy database from container
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/database_$TIMESTAMP.db"

echo "Copying database to: $OUTPUT_FILE"
docker cp "$CONTAINER_ID:$DB_PATH" "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Database extracted successfully!"
    echo ""
    echo "File: $OUTPUT_FILE"
    echo "Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
    echo ""
    echo "To view data, run:"
    echo "  sqlite3 $OUTPUT_FILE 'SELECT * FROM gpio_log;'"
else
    echo "❌ Failed to copy database"
    exit 1
fi

# Optional: Also create a CSV export
echo ""
read -p "Export to CSV as well? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CSV_FILE="$OUTPUT_DIR/gpio_log_$TIMESTAMP.csv"
    echo "Creating CSV export..."
    sqlite3 -header -csv "$OUTPUT_FILE" "SELECT * FROM gpio_log;" > "$CSV_FILE"
    echo "✓ CSV exported to: $CSV_FILE"
fi

echo ""
echo "=== Complete ==="
