
import os
import time
import threading
import dask
import dask.dataframe as dd
import pandas as pd
import psutil

file_path = os.path.join("data", "big_synthetic.csv")

if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

file_size_gb = os.path.getsize(file_path) / 1e9
process = psutil.Process(os.getpid())

ram_before = process.memory_info().rss / (1024 ** 2)
peak_ram = [ram_before]
stop_monitor = threading.Event()

def monitor_memory():
    while not stop_monitor.wait(0.1):
        try:
            current = process.memory_info().rss / (1024 ** 2)
            peak_ram[0] = max(peak_ram[0], current)
        except psutil.Error:
            break

print("File size:", round(file_size_gb, 3), "GB")
print("Method: Dask DataFrame")
print("Block size: 32 MB")
print("Scheduler: threads, 2 workers")

# Create the Dask DataFrame.
# This builds the task graph; it does not read the whole file immediately.
ddf = dd.read_csv(
    file_path,
    usecols=["temperature", "humidity"],
    blocksize="32MB"
)

print("Number of partitions:", ddf.npartitions)

# Define computations. They are lazy until dask.compute() is called.
temperature_sum = ddf["temperature"].sum()
humidity_sum = ddf["humidity"].sum()
row_count = ddf["temperature"].count()
start_time = time.perf_counter()
monitor = threading.Thread(target=monitor_memory, daemon=True)
monitor.start()

try:
    temp_total, humidity_total, total_rows = dask.compute(
        temperature_sum,
        humidity_sum,
        row_count,
        scheduler="threads",
        num_workers=2
    )
finally:
    stop_monitor.set()
    monitor.join()

execution_time = time.perf_counter() - start_time
ram_after = process.memory_info().rss / (1024 ** 2)

if total_rows == 0:
    raise ValueError("The CSV file contains no data rows.")

mean_temperature = float(temp_total) / int(total_rows)
mean_humidity = float(humidity_total) / int(total_rows)

print("\n--- DASK RESULTS ---")
print("Total rows:", int(total_rows))
print("Mean temperature:", round(mean_temperature, 4))
print("Mean humidity:", round(mean_humidity, 4))
print("Execution time:", round(execution_time, 2), "seconds")
print("RAM before:", round(ram_before, 2), "MB")
print("RAM after:", round(ram_after, 2), "MB")
print("Peak RAM observed:", round(peak_ram[0], 2), "MB")

os.makedirs("results", exist_ok=True)

results = pd.DataFrame([{
    "method": "Dask",
    "file_size_GB": round(file_size_gb, 3),
    "rows_processed": int(total_rows),
    "partitions": ddf.npartitions,
    "block_size": "32MB",
    "mean_temperature": mean_temperature,
    "mean_humidity": mean_humidity,
    "execution_time_seconds": execution_time,
    "ram_before_MB": ram_before,
    "ram_after_MB": ram_after,
    "peak_ram_observed_MB": peak_ram[0]
}])

results.to_csv("results/dask_results.csv", index=False)
print("\nResults saved to results/dask_results.csv")
