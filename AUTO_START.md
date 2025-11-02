# Auto-Start Configuration

The web viewer is configured to automatically start on Arduino UNO Q boot.

## How It Works

### Startup Script
Location: `~/start_web_viewer.sh`

```bash
#!/bin/bash
cd ~/Desktop/"Python Scripts"
python3 web_viewer.py > ~/flask.log 2>&1 &
echo "Web viewer started (PID: $!)"
```

### Crontab Entry
The script is triggered on boot via crontab:
```
@reboot sleep 10 && /home/arduino/start_web_viewer.sh
```

## Manual Control

### Start Web Viewer
```bash
~/start_web_viewer.sh
```

### Stop Web Viewer
```bash
pkill -f web_viewer.py
```

### Check Status
```bash
ps aux | grep web_viewer
# or
curl http://localhost:5000/api/stats
```

### View Logs
```bash
tail -f ~/flask.log
```

## Troubleshooting

### Web viewer not starting after reboot
1. Check if crontab entry exists:
   ```bash
   crontab -l
   ```
2. Check the log file:
   ```bash
   cat ~/flask.log
   ```
3. Manually run the startup script:
   ```bash
   ~/start_web_viewer.sh
   ```

### Check if it's running
```bash
curl http://localhost:5000/api/data
```

If you get a response, it's running!

## Modifying the Auto-Start

### Disable auto-start
```bash
crontab -e
# Remove or comment out the @reboot line
```

### Change log location
Edit `~/start_web_viewer.sh` and change the log path:
```bash
python3 web_viewer.py > /path/to/your/log.log 2>&1 &
```

### Change startup delay
Edit crontab:
```bash
crontab -e
# Change sleep 10 to desired seconds
@reboot sleep 30 && /home/arduino/start_web_viewer.sh
```

## Installed on Arduino

The following files are deployed on your Arduino UNO Q:

- **`~/start_web_viewer.sh`** - Startup script
- **`~/flask.log`** - Web viewer log file
- **Crontab entry** - Triggers on boot

The web viewer will automatically start 10 seconds after boot and be accessible at:
**http://192.168.0.125:5000**
