#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
import sqlite3
import subprocess
import os

app = Flask(__name__)

DATABASE = os.path.expanduser("~/Desktop/gpio_data.db")

def export_fresh_data():
    """Export fresh data from Docker container"""
    try:
        # Find container
        result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        container_id = result.stdout.strip().split()[0]
        
        # Find database
        result = subprocess.run(
            ["docker", "exec", container_id, "find", "/home", "-name", "database.db"],
            capture_output=True, text=True
        )
        db_path = result.stdout.strip().split()[0]
        
        # Copy database
        with open(DATABASE, "wb") as f:
            subprocess.run(["docker", "exec", container_id, "cat", db_path], stdout=f)
        
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False

def get_db_data():
    """Fetch all data from the database"""
    try:
        # Export fresh data before reading
        export_fresh_data()
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM gpio_log")
        total = cursor.fetchone()["count"]
        
        # Get all entries
        cursor.execute("SELECT * FROM gpio_log ORDER BY id DESC LIMIT 100")
        entries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {"total": total, "entries": entries}
    except Exception as e:
        return {"error": str(e), "total": 0, "entries": []}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    """API endpoint to get fresh data - automatically exports from container"""
    return jsonify(get_db_data())

if __name__ == "__main__":
    print("Starting web viewer with auto-export enabled...")
    print("Data will be automatically exported from Docker container on each request")
    # Run on all network interfaces so you can access from other devices
    app.run(host="0.0.0.0", port=5000, debug=True)
