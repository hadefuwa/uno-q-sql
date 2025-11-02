from datetime import datetime
import time
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

# Check existing data
result = db.read("gpio_log")
print(f"✓ Existing entries: {len(result)}\n")

def log_dummy_data():
    """Continuously log dummy data every 2 seconds"""
    counter = 0
    while True:
        try:
            # Alternate between 1 and 0
            value = counter % 2

            data = {
                "timestamp": datetime.now().isoformat(),
                "pin_state": value,
                "led_state": value
            }
            db.store("gpio_log", data)

            counter += 1
            all_data = db.read("gpio_log")
            print(f"Entry #{len(all_data)}: pin={value}, led={value} [total logged this session: {counter}]")

            time.sleep(2)  # Log every 2 seconds
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

print("Database ready. Starting dummy data logging...\n")

# Start logging dummy data in the background
import threading
logger_thread = threading.Thread(target=log_dummy_data, daemon=True)
logger_thread.start()

# Keep app running - this launches and maintains the Docker container
App.run()