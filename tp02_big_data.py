
import os
import pandas as pd

# Create the required folders
os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Path of the test dataset
file_path = "data/test_data.csv"

# Create a small dataset with 10,000 rows
if not os.path.exists(file_path):
    df = pd.DataFrame({
        "temperature": range(1, 10001),
        "humidity": range(40, 10040),
        "sensor_id": range(10000)
    })

    df.to_csv(file_path, index=False)
    print("Dataset created successfully!")

# Display information about the file
file_size_kb = os.path.getsize(file_path) / 1024

print("File path:", file_path)
print("File size:", round(file_size_kb, 2), "KB")

# Read the dataset using Pandas
data = pd.read_csv(file_path)

print("Number of rows:", len(data))
print("First 5 rows:")
print(data.head())

print("Mean temperature:", data["temperature"].mean())

# Task 2: Process data in chunks

print("\n--- Pandas Chunking ---")

total_temperature = 0
total_rows = 0
chunk_size = 1000

for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    total_temperature += chunk["temperature"].sum()
    total_rows += chunk["temperature"].count()

mean_temperature = total_temperature / total_rows

print("Chunk size:", chunk_size)
print("Rows processed:", total_rows)
print("Total temperature:", total_temperature)
print("Mean temperature:", mean_temperature)

