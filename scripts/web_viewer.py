#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.expanduser("~/Desktop/gpio_data.db")

def get_db_data():
    """Fetch all data from the database"""
    try:
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
    """API endpoint to get fresh data"""
    return jsonify(get_db_data())

if __name__ == "__main__":
    # Run on all network interfaces so you can access from other devices
    app.run(host="0.0.0.0", port=5000, debug=True)
