# Database Extraction Guide for Arduino UNO Q

## Quick Reference Commands

### 1. Find Your Container
```bash
# List all running containers
docker ps

# Find container by name/image
docker ps | grep sqlstore

# Get the container ID (use this for commands below)
CONTAINER_ID=$(docker ps -q | head -n 1)
echo $CONTAINER_ID
```

### 2. Locate the Database File
```bash
# Find database.db in the container
docker exec $CONTAINER_ID find / -name "database.db" 2>/dev/null

# Common locations:
docker exec $CONTAINER_ID ls -la /app/
docker exec $CONTAINER_ID ls -la /data/
docker exec $CONTAINER_ID ls -la /root/
docker exec $CONTAINER_ID ls -la /tmp/
```

### 3. Copy Database to Your Debian System
```bash
# Replace CONTAINER_ID and /path/to/database.db with actual values
docker cp CONTAINER_ID:/path/to/database.db ~/database.db

# Example:
docker cp abc123:/app/database.db ~/database.db
```

### 4. View the Data
```bash
# Install sqlite3 if needed
sudo apt-get update && sudo apt-get install -y sqlite3

# View all entries
sqlite3 ~/database.db "SELECT * FROM gpio_log;"

# Count entries
sqlite3 ~/database.db "SELECT COUNT(*) FROM gpio_log;"

# Export to CSV
sqlite3 -header -csv ~/database.db "SELECT * FROM gpio_log;" > ~/gpio_log.csv

# View last 10 entries
sqlite3 ~/database.db "SELECT * FROM gpio_log ORDER BY id DESC LIMIT 10;"
```

## Method 1: Using the Enhanced Python Code

If you update your brick with `enhanced_brick.py`:

1. The brick adds new callable functions:
   - `export_database()` - Copies DB to /tmp
   - `export_to_csv()` - Exports as CSV
   - `get_all_data()` - Returns all data

2. You can call these from your main app via Bridge.call()

## Method 2: Using the Shell Script

1. Copy `extract_db.sh` to your Arduino UNO Q
2. Make it executable:
   ```bash
   chmod +x extract_db.sh
   ```
3. Run it:
   ```bash
   ./extract_db.sh
   ```

The script will:
- Find your container automatically
- Locate database.db
- Copy it to ~/arduino_data/
- Optionally export to CSV

## Method 3: Docker Volume Mounting (Permanent Solution)

Modify your brick to use a mounted volume so the database is directly accessible:

```python
# In your brick's Docker configuration or when creating SQLStore
db = SQLStore("/data/database.db")  # /data should be mounted to host
```

Then run your app with volume mount:
```bash
docker run -v ~/arduino_data:/data your-app-image
```

This way database.db is always at `~/arduino_data/database.db` on your host system.

## Method 4: Live Access While Container is Running

Access the database directly while the container runs:

```bash
# Start sqlite3 inside the container
docker exec -it CONTAINER_ID sqlite3 /path/to/database.db

# Then run SQL commands:
sqlite> SELECT * FROM gpio_log;
sqlite> .exit
```

## Automated Periodic Export

Create a cron job to export data every hour:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths):
0 * * * * docker cp $(docker ps -q | head -n 1):/app/database.db ~/backups/database_$(date +\%Y\%m\%d_\%H\%M).db
```

## Troubleshooting

### Container not found
- Check if your app is running: `docker ps`
- Check all containers including stopped: `docker ps -a`
- Make sure the brick is deployed and running

### Database file not found
- The database might be in a different location
- Check container filesystem: `docker exec CONTAINER_ID ls -R / | grep database.db`
- Verify your Python code is actually creating the database

### Permission denied
- Try with sudo: `sudo docker cp ...`
- Check file permissions in container: `docker exec CONTAINER_ID ls -la /path/to/database.db`

### Database is locked
- This happens if the Python app has the database open
- The SQLite database can be read even while locked
- For write operations, you may need to stop the container temporarily

## Example Complete Workflow

```bash
# 1. Find container
CONTAINER_ID=$(docker ps -q | head -n 1)

# 2. Find database
DB_PATH=$(docker exec $CONTAINER_ID find / -name "database.db" 2>/dev/null | head -n 1)

# 3. Copy to host
mkdir -p ~/arduino_data
docker cp $CONTAINER_ID:$DB_PATH ~/arduino_data/database.db

# 4. View data
sqlite3 ~/arduino_data/database.db "SELECT * FROM gpio_log ORDER BY timestamp DESC LIMIT 10;"

# 5. Export to CSV
sqlite3 -header -csv ~/arduino_data/database.db "SELECT * FROM gpio_log;" > ~/arduino_data/gpio_log.csv

echo "Done! Data is at ~/arduino_data/"
```
