#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import subprocess
import os
from datetime import datetime
import csv
import io

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

def clear_container_database():
    """Clear the database in the Docker container"""
    try:
        result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        container_id = result.stdout.strip().split()[0]

        result = subprocess.run(
            ["docker", "exec", container_id, "find", "/home", "-name", "database.db"],
            capture_output=True, text=True
        )
        db_path = result.stdout.strip().split()[0]

        # Clear the database by deleting all rows
        clear_cmd = f"sqlite3 {db_path} 'DELETE FROM gpio_log;'"
        subprocess.run(
            ["docker", "exec", container_id, "sh", "-c", clear_cmd],
            check=True
        )

        return True
    except Exception as e:
        print(f"Clear error: {e}")
        return False

def get_db_data(limit=100):
    """Fetch data from the database"""
    try:
        # Export fresh data before reading
        export_fresh_data()

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM gpio_log")
        total = cursor.fetchone()["count"]

        # Get entries with limit
        cursor.execute(f"SELECT * FROM gpio_log ORDER BY id DESC LIMIT {limit}")
        entries = [dict(row) for row in cursor.fetchall()]

        # Get first and last timestamp
        first_ts = None
        last_ts = None
        if total > 0:
            cursor.execute("SELECT timestamp FROM gpio_log ORDER BY id LIMIT 1")
            first_ts = cursor.fetchone()["timestamp"]
            cursor.execute("SELECT timestamp FROM gpio_log ORDER BY id DESC LIMIT 1")
            last_ts = cursor.fetchone()["timestamp"]

        conn.close()

        return {
            "total": total,
            "entries": entries,
            "first_timestamp": first_ts,
            "last_timestamp": last_ts
        }
    except Exception as e:
        return {"error": str(e), "total": 0, "entries": [], "first_timestamp": None, "last_timestamp": None}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    """API endpoint to get fresh data - automatically exports from container"""
    limit = request.args.get("limit", 100, type=int)
    return jsonify(get_db_data(limit))

@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear all data from the database"""
    try:
        success = clear_container_database()
        if success:
            # Also clear the exported file
            if os.path.exists(DATABASE):
                os.remove(DATABASE)
            return jsonify({"success": True, "message": "Database cleared successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to clear database"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/export/csv")
def api_export_csv():
    """Export all data as CSV"""
    try:
        export_fresh_data()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gpio_log ORDER BY id")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute("PRAGMA table_info(gpio_log)")
        columns = [col[1] for col in cursor.fetchall()]

        conn.close()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)

        # Convert to bytes
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"gpio_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/stats")
def api_stats():
    """Get database statistics"""
    try:
        export_fresh_data()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Total entries
        cursor.execute("SELECT COUNT(*) as count FROM gpio_log")
        total = cursor.fetchone()[0]

        # Count by pin state
        cursor.execute("SELECT pin_state, COUNT(*) as count FROM gpio_log GROUP BY pin_state")
        pin_counts = dict(cursor.fetchall())

        # Count by led state
        cursor.execute("SELECT led_state, COUNT(*) as count FROM gpio_log GROUP BY led_state")
        led_counts = dict(cursor.fetchall())

        # Database file size
        db_size = os.path.getsize(DATABASE) if os.path.exists(DATABASE) else 0

        conn.close()

        return jsonify({
            "total_entries": total,
            "pin_state_counts": pin_counts,
            "led_state_counts": led_counts,
            "database_size_kb": round(db_size / 1024, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print("Starting enhanced web viewer...")
    print("Features:")
    print("  - Auto-export from Docker container")
    print("  - Clear database")
    print("  - Export to CSV")
    print("  - Statistics dashboard")
    print("")
    app.run(host="0.0.0.0", port=5000, debug=True)
