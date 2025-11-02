# Arduino UNO Q SQLite Data Logging System

## Overview

This project implements a SQLite database logging system for the Arduino UNO Q that runs inside a Docker container. The main challenge was accessing the database data from the host Debian system, as Docker containers isolate their filesystems.

## The Problem

The Arduino UNO Q platform uses **Bricks** - Python code packages that run as separate processes in Docker containers. When using the `SQLStore` brick to log data to a SQLite database:

1. The database file (`database.db`) exists **only inside the Docker container**
2. The container's filesystem is **isolated** from the host Debian system
3. Docker volume mounting (the typical solution) **does not work** with Arduino's brick system
4. Data needed to be extracted from the container to be accessible on the host

### Key Findings

Through testing, we discovered:
- **Data persists across Arduino reboots** - The Docker container preserves the database even after stopping/restarting
- The database is located at: `/home/arduino/ArduinoApps/<app_name>/data/dbstorage_sqlstore/database.db` inside the container
- `docker cp` has issues with certain paths, but using `docker exec` with `cat` works reliably

## Solution Architecture

### 1. Data Logging (Arduino UNO Q)
- **Files:** `main.py` (Python brick) + `sketch.ino` (microcontroller code)
- Logs real GPIO data from pin 2 via Bridge communication
- Microcontroller sends data every 5 seconds
- Uses Arduino's `SQLStore` brick inside a Docker container
- Data accumulates and persists across reboots

### 2. Data Export Script (Debian Host)
- **Location:** `~/Desktop/Python Scripts/export_gpio_data.py` (on Arduino)
- Automatically finds the running Docker container
- Extracts the database file using `docker exec` and `cat`
- Copies data to `~/Desktop/gpio_data.db` (accessible on host)

### 3. Web Viewer (Debian Host)
- **Location:** `~/Desktop/Python Scripts/web_viewer.py` (on Arduino)
- Flask-based web application with enhanced features:
  - Auto-export from Docker container on every refresh
  - Clear all data with confirmation dialog
  - Export to CSV with timestamp
  - Statistics dashboard (entry counts, file size, state distribution)
  - Auto-refreshes every 5 seconds
  - Accessible from any device on the network

## Files in This Directory

### Core Application Files

- **`main.py`** - Python brick code (runs in Docker container)
  - Receives data from microcontroller via Bridge
  - Logs GPIO states to SQLite database
  - Works with sketch.ino for real hardware monitoring

- **`sketch.ino`** - Microcontroller code (runs on RP2350)
  - Reads GPIO input from pin 2
  - Controls LED based on input (blinks when HIGH, off when LOW)
  - Sends data to Python via Bridge every 5 seconds
  - See [SKETCH_INFO.md](SKETCH_INFO.md) for details

### Helper Scripts (Deploy to Arduino)

- **`scripts/export_gpio_data.py`** - Manual database extractor (optional, web viewer auto-exports)
- **`scripts/web_viewer.py`** - Enhanced Flask web server with:
  - Automatic database export from container
  - Clear database functionality
  - CSV export with timestamp
  - Real-time statistics
- **`templates/index.html`** - Modern web interface with color-coded stats and controls

### Documentation

- **`README.md`** - This file, comprehensive project documentation
- **`QUICKSTART.md`** - Quick reference guide for daily use
- **`INSTALL.md`** - Step-by-step installation guide for beginners
- **`SKETCH_INFO.md`** - Arduino sketch details and hardware setup

## Setup Instructions

### Prerequisites

On the Arduino UNO Q:
- Python 3 with Flask installed
- Docker running (managed by Arduino system)
- SSH access enabled

### Step 1: Deploy the Main Application

1. Copy `main.py` to your Arduino project
2. Deploy the app through Arduino Cloud Editor or CLI
3. The app will start logging data every 2 seconds

### Step 2: Set Up the Export Script

Already configured on the Arduino at:
```
~/Desktop/Python Scripts/export_gpio_data.py
```

To use it:
```bash
cd ~/Desktop/"Python Scripts"
python3 export_gpio_data.py
```

This creates `~/Desktop/gpio_data.db` with the latest data.

### Step 3: Start the Web Viewer

On the Arduino UNO Q:
```bash
cd ~/Desktop/"Python Scripts"
python3 web_viewer.py
```

Then access from any device on your network:
```
http://192.168.0.125:5000
```
(Replace with your Arduino's actual IP address)

## Usage

### Viewing Data via Web Browser

1. Ensure the export script has run at least once:
   ```bash
   python3 export_gpio_data.py
   ```

2. Start the web server:
   ```bash
   python3 web_viewer.py
   ```

3. Open browser to: `http://<arduino_ip>:5000`

4. The page shows:
   - Total entries count
   - Latest pin and LED states
   - Table of last 100 entries
   - Auto-refreshes every 5 seconds

### Manual Database Access

Export the database:
```bash
python3 ~/Desktop/"Python Scripts"/export_gpio_data.py
```

Query with sqlite3:
```bash
sqlite3 ~/Desktop/gpio_data.db "SELECT * FROM gpio_log ORDER BY id DESC LIMIT 10;"
```

Export to CSV:
```bash
sqlite3 -header -csv ~/Desktop/gpio_data.db "SELECT * FROM gpio_log;" > gpio_log.csv
```

## Database Schema

Table: `gpio_log`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-incrementing entry ID |
| timestamp | TEXT | ISO format timestamp |
| pin_state | INTEGER | GPIO pin state (0 or 1) |
| led_state | INTEGER | LED state (0 or 1) |

## Network Access

The web viewer runs on port 5000 and is accessible from:
- **Localhost:** http://localhost:5000 (from Arduino)
- **Network:** http://192.168.0.125:5000 (from other devices)

Find your Arduino's IP:
```bash
hostname -I | awk '{print $1}'
```

## Troubleshooting

### Container Not Found
```bash
docker ps  # Check if container is running
```
If no containers, redeploy your Arduino app.

### Database Not Found
The container might have a different name. Check:
```bash
docker ps --format "{{.Names}}"
```

### Web Server Won't Start
Check if Flask is installed:
```bash
python3 -c "import flask; print('OK')"
```

If not:
```bash
sudo apt-get install python3-flask
```

### Data Not Updating
Run the export script again:
```bash
python3 ~/Desktop/"Python Scripts"/export_gpio_data.py
```
The web viewer reads from the exported database file.

## Technical Notes

### Why Not Docker Volumes?
Standard Docker practice uses volume mounts (`-v`) to share data between container and host. However, Arduino's brick system manages container creation automatically, and we don't have control over volume mount configuration.

### Why Use `cat` Instead of `docker cp`?
`docker cp` has issues with certain path structures in Arduino's container setup. Using `docker exec <container> cat <path>` and redirecting to a file is more reliable.

### Data Persistence
The Docker container is **persistent**, not ephemeral. Data survives:
- ✅ Arduino reboots
- ✅ Container restarts
- ✅ App restarts
- ❌ App redeployment (creates new container)

## Future Enhancements

Possible improvements:
- Real-time data streaming (WebSocket instead of polling)
- Direct container-to-host database connection
- Automatic scheduled exports (cron job)
- Data visualization graphs/charts
- Export to other formats (JSON, Excel)
- Authentication for web access

## Project Timeline

This solution was developed through iterative problem-solving:
1. Identified Docker isolation issue
2. Confirmed data persistence across reboots
3. Tested extraction methods (docker cp vs docker exec)
4. Built Python export script
5. Created Flask web interface
6. Documented the complete solution

## Author Notes

This project demonstrates a practical workaround for Docker filesystem isolation when standard volume mounting isn't available. The solution uses native Docker commands accessible from the host system to bridge the gap between containerized and host environments.
