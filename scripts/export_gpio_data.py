#!/usr/bin/env python3
import subprocess
import os

desktop = os.path.expanduser("~/Desktop")
output_db = os.path.join(desktop, "gpio_data.db")

print("=== GPIO Data Exporter ===\n")

# Find container
result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
container_id = result.stdout.strip().split()[0]
print(f"Container: {container_id}")

# Find database
result = subprocess.run(["docker", "exec", container_id, "find", "/home", "-name", "database.db"], capture_output=True, text=True)
db_path = result.stdout.strip().split()[0]
print(f"Database: {db_path}")

# Copy database
print(f"\nCopying to: {output_db}")
with open(output_db, "wb") as f:
    subprocess.run(["docker", "exec", container_id, "cat", db_path], stdout=f)

# Show stats
result = subprocess.run(["sqlite3", output_db, "SELECT COUNT(*) FROM gpio_log;"], capture_output=True, text=True)
print(f"\nTotal entries: {result.stdout.strip()}")
print(f"Saved to: {output_db}")
