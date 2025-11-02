from datetime import datetime
import time
import shutil
import os
from arduino.app_utils import App
from arduino.app_bricks.dbstorage_sqlstore import SQLStore

db = SQLStore("database.db")

columns = {
    "id": "INTEGER PRIMARY KEY",
    "timestamp": "TEXT",
    "pin_state": "INTEGER",
    "led_state": "INTEGER"
}
db.create_table("gpio_log", columns)

# Write test entry
test_data = {"timestamp": datetime.now().isoformat(), "pin_state": 0, "led_state": 0}
db.store("gpio_log", test_data)

result = db.read("gpio_log")
print(f"✓ Test entry: {result}\n")

def log_data(pin_state, led_state):
    """Called by microcontroller via Bridge.call()"""
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "pin_state": int(pin_state),
            "led_state": int(led_state)
        }
        db.store("gpio_log", data)
        all_data = db.read("gpio_log")
        print(f"Entry #{len(all_data)}: pin={pin_state}, led={led_state}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def export_database(output_path="/tmp/database_export.db"):
    """Export the database file to a location accessible from the host"""
    try:
        # The database file is typically at the brick's working directory
        source_db = "database.db"

        # Copy to /tmp which can be mounted/accessed from host
        shutil.copy2(source_db, output_path)
        print(f"✓ Database exported to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Export error: {e}")
        return None

def export_to_csv(output_path="/tmp/gpio_log.csv"):
    """Export data as CSV for easier access"""
    try:
        import csv

        all_data = db.read("gpio_log")

        with open(output_path, 'w', newline='') as csvfile:
            if all_data:
                fieldnames = all_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_data)

        print(f"✓ Data exported to CSV: {output_path}")
        print(f"✓ Total entries: {len(all_data)}")
        return output_path
    except Exception as e:
        print(f"CSV export error: {e}")
        return None

def get_all_data():
    """Return all data as JSON-serializable format"""
    try:
        all_data = db.read("gpio_log")
        print(f"✓ Retrieved {len(all_data)} entries")
        return all_data
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []

print("Database ready. App running...")
print("Available functions:")
print("  - log_data(pin_state, led_state)")
print("  - export_database(output_path)")
print("  - export_to_csv(output_path)")
print("  - get_all_data()\n")

# Keep app running - this launches and maintains the Docker container
App.run()
