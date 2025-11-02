# Installation Guide

## For Beginners: Copy This Project to Your Arduino UNO Q

### Prerequisites

- Arduino UNO Q board
- SSH access to your Arduino (username: arduino)
- Basic familiarity with terminal commands

---

## Step 1: Deploy the Main Application

### 1.1 Get the Code
Clone or download this repository to your computer:
```bash
git clone https://github.com/hadefuwa/uno-q-sql.git
cd uno-q-sql
```

### 1.2 Deploy to Arduino
1. Open Arduino Cloud Editor or Arduino Lab
2. Create a new App project called `sql_app`
3. Copy the contents of `main.py` into your project's `main.py`
4. Deploy the app to your Arduino UNO Q
5. The app will start logging data every 2 seconds

---

## Step 2: Set Up the Helper Scripts

### 2.1 SSH into Your Arduino
```bash
ssh arduino@<your-arduino-ip>
# Password: (your Arduino password)
```

### 2.2 Create Scripts Directory
```bash
mkdir -p ~/Desktop/"Python Scripts"
mkdir -p ~/Desktop/"Python Scripts"/templates
```

### 2.3 Copy the Scripts
On your computer, copy the files to Arduino:

```bash
# Copy export script
scp scripts/export_gpio_data.py arduino@<arduino-ip>:~/Desktop/"Python Scripts"/

# Copy web viewer
scp scripts/web_viewer.py arduino@<arduino-ip>:~/Desktop/"Python Scripts"/

# Copy HTML template
scp templates/index.html arduino@<arduino-ip>:~/Desktop/"Python Scripts"/templates/
```

### 2.4 Make Scripts Executable
On the Arduino:
```bash
chmod +x ~/Desktop/"Python Scripts"/*.py
```

---

## Step 3: Install Flask (if not already installed)

On your Arduino UNO Q:
```bash
sudo apt-get update
sudo apt-get install -y python3-flask
```

---

## Step 4: Test Everything

### 4.1 Check if App is Running
```bash
docker ps
```
You should see a container named something like `sql_app-main-1`

### 4.2 Export Some Data
```bash
cd ~/Desktop/"Python Scripts"
python3 export_gpio_data.py
```
You should see: "Total entries: X" and "Saved to: /home/arduino/Desktop/gpio_data.db"

### 4.3 Start the Web Viewer
```bash
python3 web_viewer.py
```

### 4.4 Access in Browser
Open your browser to:
```
http://<your-arduino-ip>:5000
```

You should see the GPIO Data Monitor with live data!

---

## Quick Reference

### Find Your Arduino's IP
```bash
hostname -I | awk '{print $1}'
```

### Stop the Web Server
Press `Ctrl+C` in the terminal where it's running

### Export Fresh Data
```bash
python3 ~/Desktop/"Python Scripts"/export_gpio_data.py
```

### View Data Manually
```bash
sqlite3 ~/Desktop/gpio_data.db "SELECT * FROM gpio_log ORDER BY id DESC LIMIT 10;"
```

---

## Troubleshooting

### "No such file or directory"
Make sure you created the directories:
```bash
mkdir -p ~/Desktop/"Python Scripts"/templates
```

### "Module not found: flask"
Install Flask:
```bash
sudo apt-get install -y python3-flask
```

### "Container not found"
Your app isn't running. Redeploy it from Arduino Cloud Editor.

### Can't access web page
1. Check the Arduino's IP: `hostname -I`
2. Make sure Flask is running: Look for "Running on http://0.0.0.0:5000"
3. Check firewall settings if accessing from another device

---

## Next Steps

Once everything is working:
1. Read [QUICKSTART.md](QUICKSTART.md) for daily usage
2. Check [README.md](README.md) for detailed technical information
3. See [EXTRACTION_GUIDE.md](EXTRACTION_GUIDE.md) for advanced database access

---

## Need Help?

- Check the documentation files in this repo
- Review the troubleshooting section above
- Open an issue on GitHub: https://github.com/hadefuwa/uno-q-sql/issues

---

**Congratulations!** You now have a working SQLite logging system on your Arduino UNO Q with web-based viewing! 🎉
