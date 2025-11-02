from datetime import datetime
from arduino.app_utils import App, Bridge
from arduino.app_bricks.dbstorage_sqlstore import SQLStore

db = SQLStore("database.db")

columns = {
    "id": "INTEGER PRIMARY KEY",
    "timestamp": "TEXT",
    "pin_state": "INTEGER",
    "led_state": "INTEGER"
}
db.create_table("gpio_log", columns)

# Check existing data
result = db.read("gpio_log")
print(f"✓ Existing entries: {len(result)}\n")

def log_data(pin_state, led_state):
    """Called by microcontroller via Bridge.call() every 5 seconds"""
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

# Provide the log_data function to the microcontroller
Bridge.provide("log_data", log_data)

print("Database ready. Waiting for data from microcontroller...\n")

# Keep app running - this launches and maintains the Docker container
App.run()