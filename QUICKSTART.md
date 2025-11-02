# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Deploy the App
Copy `main.py` to your Arduino UNO Q project and deploy it. The app will start logging data automatically.

### Step 2: Export the Data
On your Arduino UNO Q, run:
```bash
python3 ~/Desktop/"Python Scripts"/export_gpio_data.py
```

### Step 3: View in Browser
Start the web server:
```bash
python3 ~/Desktop/"Python Scripts"/web_viewer.py
```

Then open: **http://192.168.0.125:5000** (or your Arduino's IP)

---

## 📊 What You'll See

The web interface shows:
- **Total Entries** - Number of logged records
- **Latest States** - Current pin and LED values
- **Recent Data** - Table of last 100 entries
- **Auto-refresh** - Updates every 5 seconds

---

## 🔄 Regular Use

### To get fresh data:
```bash
# Export latest data from Docker container
python3 ~/Desktop/"Python Scripts"/export_gpio_data.py

# Then refresh your browser
```

### To query data manually:
```bash
# View last 10 entries
sqlite3 ~/Desktop/gpio_data.db "SELECT * FROM gpio_log ORDER BY id DESC LIMIT 10;"

# Count total entries
sqlite3 ~/Desktop/gpio_data.db "SELECT COUNT(*) FROM gpio_log;"

# Export to CSV
sqlite3 -header -csv ~/Desktop/gpio_data.db "SELECT * FROM gpio_log;" > data.csv
```

---

## ❓ Common Issues

**"Container not found"**
→ Make sure your Arduino app is running: `docker ps`

**"Database not found"**
→ Run the export script first: `python3 export_gpio_data.py`

**"Can't access web page"**
→ Check Arduino's IP: `hostname -I | awk '{print $1}'`

---

## 📁 File Locations

| What | Where |
|------|-------|
| Main app code | Your Arduino project (main.py) |
| Export script | ~/Desktop/Python Scripts/export_gpio_data.py |
| Web viewer | ~/Desktop/Python Scripts/web_viewer.py |
| Exported database | ~/Desktop/gpio_data.db |
| Container database | Inside Docker (auto-managed) |

---

For detailed information, see [README.md](README.md)
