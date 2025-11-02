# Arduino Sketch Information

## sketch.ino

This is the **microcontroller code** that runs on the Arduino UNO Q's RP2350 chip.

### What It Does

1. **Reads GPIO Input** - Monitors pin 2 for input signals
2. **Controls LED** - Blinks the built-in LED when input is HIGH
3. **Logs Data** - Calls the Python `log_data()` function every 5 seconds via Bridge
4. **Provides Functions** - Exposes `get_pin_state()` and `get_led_state()` to Python

### Hardware Setup

- **INPUT_PIN (Pin 2)** - Connect your sensor/switch here (uses internal pull-down resistor)
- **LED_BUILTIN** - Uses the onboard LED for visual feedback

### How It Works with Python

The sketch uses Arduino's **Bridge** system to communicate with the Python brick:

```cpp
// In loop(), every 5 seconds:
Bridge.call("log_data", inputHigh, ledState == LOW);
```

This calls the Python function:
```python
def log_data(pin_state, led_state):
    # Stores data in SQLite database
```

### Using This Sketch

1. Open the Arduino Cloud Editor or Arduino Lab
2. Create a new **App** project
3. Add your Python code to `main.py`
4. Add this sketch code to `sketch.ino`
5. Deploy to your Arduino UNO Q

---

## Switching Between Demo and Real Hardware

### For Testing/Demo (No Hardware Required)
Use `main.py` with the dummy data generator:
- Logs alternating 0/1 values every 2 seconds
- No microcontroller code needed
- Good for testing the database and web viewer

### For Real Hardware Implementation
Use `main.py` modified for Bridge + `sketch.ino`:
- Comment out or remove the dummy data thread in `main.py`
- Uncomment the `log_data()` function
- Add `Bridge.provide("log_data", log_data)` in Python
- Deploy both files together
- Connect hardware to pin 2

---

## Example main.py for Real Hardware

```python
from datetime import datetime
import time
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

# Provide the function to the microcontroller
Bridge.provide("log_data", log_data)

print("Database ready. Waiting for microcontroller data...\n")

# Keep app running
App.run()
```

---

## Pin Reference

| Pin | Purpose | Connection |
|-----|---------|------------|
| 2 | GPIO Input | Connect sensor/switch (pull-down enabled) |
| LED_BUILTIN | Status LED | Onboard LED (no external connection needed) |

---

**Note:** The current `main.py` in the repo uses dummy data for demonstration. Modify it according to the example above when using with the sketch.
