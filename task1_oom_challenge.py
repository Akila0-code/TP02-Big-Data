import os
import sys
import time
import subprocess
import psutil

# Project paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(PROJECT_DIR, "data", "big_synthetic.csv")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")

STATUS_FILE = os.path.join(RESULTS_DIR, "task1_worker_status.txt")
REPORT_FILE = os.path.join(RESULTS_DIR, "task1_oom_report.txt")

# Safety limits for a computer with 8 GB RAM
MIN_START_RAM_MB = 1800
MIN_AVAILABLE_RAM_MB = 1000
MAX_PROCESS_RAM_MB = 2500

CHECK_INTERVAL = 0.25
REPORT_INTERVAL = 1.0


def save_worker_status(status, details=""):
    """Save the worker's actual result."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        file.write(f"STATUS={status}\n")
        file.write(f"DETAILS={details}\n")


def read_dataset():
    """Try reading the entire CSV using standard Pandas."""
    import pandas as pd

    print(
        "\nAttempting standard pd.read_csv() without chunksize...",
        flush=True
    )

    start_time = time.perf_counter()

    try:
        # Task 1: traditional reading of the complete file
        data = pd.read_csv(FILE_PATH)

        elapsed = time.perf_counter() - start_time

        details = (
            f"Rows={len(data)}, Columns={len(data.columns)}, "
            f"Time={elapsed:.2f} seconds"
        )

        print("STATUS: READ_SUCCESSFULLY", flush=True)
        print("Dataset shape:", data.shape, flush=True)
        print("Execution time:", round(elapsed, 2), "seconds", flush=True)

        save_worker_status("READ_SUCCESSFULLY", details)
        return 0

    except MemoryError as error:
        details = f"{type(error).__name__}: {error}"

        print("STATUS: MEMORY_ERROR", flush=True)
        print("Error:", details, flush=True)

        save_worker_status("MEMORY_ERROR", details)
        return 2

    except Exception as error:
        details = f"{type(error).__name__}: {error}"

        print("STATUS: OTHER_ERROR", flush=True)
        print("Error:", details, flush=True)

        save_worker_status("OTHER_ERROR", details)
        return 3


def save_final_report(
    status,
    file_size_gb,
    available_ram_before,
    peak_ram,
    elapsed_time,
    stop_reason="",
    worker_details=""
):
    """Save the experiment results to a text report."""

    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        report.write("Task 1: Traditional Pandas OOM Challenge\n")
        report.write(f"File size: {file_size_gb:.3f} GB\n")
        report.write(f"Status: {status}\n")
        report.write(
            f"Available RAM before test: "
            f"{available_ram_before:.2f} MB\n"
        )
        report.write(
            f"Peak worker RAM observed: {peak_ram:.2f} MB\n"
        )
        report.write(f"Duration: {elapsed_time:.2f} seconds\n")

        if stop_reason:
            report.write(f"Stop reason: {stop_reason}\n")

        if worker_details:
            report.write(f"Worker details: {worker_details}\n")


def main():
    if not os.path.isfile(FILE_PATH):
        print("ERROR: Dataset file not found:")
        print(FILE_PATH)
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)

    file_size_gb = os.path.getsize(FILE_PATH) / 1e9
    available_ram_before = (
        psutil.virtual_memory().available / (1024 ** 2)
    )

    print("File size:", round(file_size_gb, 3), "GB")
    print("Method: Traditional Pandas")
    print(
        "Available RAM before test:",
        round(available_ram_before, 2),
        "MB"
    )
    print("Monitoring enabled.")

    # Do not start if memory is already low
    if available_ram_before < MIN_START_RAM_MB:
        status = "NOT_STARTED_FOR_SAFETY"

        print("\nSTATUS:", status)
        print("Available RAM is too low to start safely.")
        print("Close unnecessary applications and check again.")

        save_final_report(
            status,
            file_size_gb,
            available_ram_before,
            0,
            0,
            stop_reason="Initial available RAM below safety threshold"
        )
        return

    # Remove status from a previous run
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)

    print("\nStarting the monitored read...", flush=True)

    start_time = time.perf_counter()

    # Start the read in a separate Python process.
    # Output is shown live in the same Terminal.
    child = subprocess.Popen(
        [
            sys.executable,
            "-u",
            os.path.abspath(__file__),
            "--worker"
        ],
        cwd=PROJECT_DIR
    )

    peak_ram = 0.0
    last_report_time = time.perf_counter()
    stop_reason = ""

    try:
        while child.poll() is None:
            try:
                worker_process = psutil.Process(child.pid)
                current_ram = (
                    worker_process.memory_info().rss / (1024 ** 2)
                )
            except psutil.NoSuchProcess:
                time.sleep(CHECK_INTERVAL)
                continue

            available_ram = (
                psutil.virtual_memory().available / (1024 ** 2)
            )

            peak_ram = max(peak_ram, current_ram)

            # Stop if the worker reaches the process RAM limit
            if current_ram >= MAX_PROCESS_RAM_MB:
                stop_reason = (
                    "Worker reached the process RAM safety limit."
                )
                break

            # Stop if system memory becomes too low
            if available_ram < MIN_AVAILABLE_RAM_MB:
                stop_reason = (
                    "Available system RAM fell below the safety limit."
                )
                break

            # Print progress once per second
            now = time.perf_counter()

            if now - last_report_time >= REPORT_INTERVAL:
                print(
                    f"Monitoring | Worker RAM: {current_ram:.0f} MB"
                    f" | Available system RAM: {available_ram:.0f} MB",
                    flush=True
                )
                last_report_time = now

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        stop_reason = "Interrupted by the user using Ctrl+C."

    # Terminate the worker if a safety limit was reached
    if stop_reason and child.poll() is None:
        child.terminate()

    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()

    elapsed_time = time.perf_counter() - start_time

    worker_status = ""
    worker_details = ""

    if os.path.isfile(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("STATUS="):
                    worker_status = line.strip().split("=", 1)[1]
                elif line.startswith("DETAILS="):
                    worker_details = line.strip().split("=", 1)[1]

    if stop_reason:
        status = "STOPPED_BY_SAFETY_MONITOR"
    elif worker_status:
        status = worker_status
    else:
        status = "WORKER_EXITED_WITHOUT_RESULT"

    print("\n--- TASK 1 SUMMARY ---")
    print("Status:", status)
    print("Execution duration:", round(elapsed_time, 2), "seconds")
    print("Peak worker RAM observed:", round(peak_ram, 2), "MB")

    if stop_reason:
        print("Reason:", stop_reason)
        print("This does NOT prove that MemoryError occurred.")

    if worker_details:
        print("Details:", worker_details)

    save_final_report(
        status,
        file_size_gb,
        available_ram_before,
        peak_ram,
        elapsed_time,
        stop_reason,
        worker_details
    )

    print("\nReport saved to:", REPORT_FILE)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        sys.exit(read_dataset())
    else:
        main()