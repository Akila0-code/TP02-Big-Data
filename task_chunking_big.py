
import os
import time
import psutil
import pandas as pd

# Path to the large CSV file
file_path = os.path.join("data", "big_synthetic.csv")

if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

file_size_gb = os.path.getsize(file_path) / 1e9

print("File size:", round(file_size_gb, 3), "GB")
print("Method: Pandas Chunking")
print("Chunk size: 100,000 rows")

process = psutil.Process(os.getpid())
ram_before = process.memory_info().rss / (1024 ** 2)
peak_ram = ram_before

total_temperature = 0
total_humidity = 0
total_rows = 0
chunk_count = 0

start_time = time.perf_counter()

# Read only the numerical columns needed for the analysis
for chunk in pd.read_csv(
    file_path,
    usecols=["temperature", "humidity"],
    chunksize=100_000
):
    total_temperature += chunk["temperature"].sum()
    total_humidity += chunk["humidity"].sum()
    total_rows += len(chunk)
    chunk_count += 1

    current_ram = process.memory_info().rss / (1024 ** 2)
    peak_ram = max(peak_ram, current_ram)

    if chunk_count % 50 == 0:
        print(
            "Chunks:", chunk_count,
            "| Rows processed:", total_rows,
            "| Peak RAM observed:", round(peak_ram, 2), "MB"
        )

end_time = time.perf_counter()

ram_after = process.memory_info().rss / (1024 ** 2)

mean_temperature = total_temperature / total_rows
mean_humidity = total_humidity / total_rows
elapsed_time = end_time - start_time

print("\n--- RESULTS ---")
print("Total rows:", total_rows)
print("Number of chunks:", chunk_count)
print("Mean temperature:", round(mean_temperature, 4))
print("Mean humidity:", round(mean_humidity, 4))
print("Execution time:", round(elapsed_time, 2), "seconds")
print("RAM before:", round(ram_before, 2), "MB")
print("RAM after:", round(ram_after, 2), "MB")
print("Peak RAM observed:", round(peak_ram, 2), "MB")

# Save the experiment results
os.makedirs("results", exist_ok=True)

results = pd.DataFrame([{
    "method": "Pandas Chunking",
    "file_size_GB": round(file_size_gb, 3),
    "rows_processed": total_rows,
    "chunks": chunk_count,
    "chunk_size": 100_000,
    "mean_temperature": mean_temperature,
    "mean_humidity": mean_humidity,
    "execution_time_seconds": elapsed_time,
    "ram_before_MB": ram_before,
    "ram_after_MB": ram_after,
    "peak_ram_observed_MB": peak_ram
}])

results.to_csv("results/chunking_results.csv", index=False)
print("\nResults saved to results/chunking_results.csv")
