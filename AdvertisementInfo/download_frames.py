import subprocess
import os
import requests
import time
from datetime import timedelta

# Open log file for writing
log_file_path = "download_log.txt"
log_file = open(log_file_path, "w", encoding="utf-8")

def log(message):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    print(full_message)             # Optional: Print to terminal
    log_file.write(full_message + "\n")
    log_file.flush()                # Ensure it's written immediately

# Track time
start_time = time.time()

# Constants
base_url = "https://storage.googleapis.com/data.gdeltproject.org/tmp_odutvnewsanalysis/"
list_url = base_url + "LIST.TXT"
download_dir = "gdelt_ttxt_files"
os.makedirs(download_dir, exist_ok=True)

# Get LIST.TXT
response = requests.get(list_url)
if response.status_code != 200:
    log(f"❌ Failed to fetch LIST.TXT: Status {response.status_code}")
    log_file.close()
    exit()

# Parse URLs
lines = response.text.strip().splitlines()
file_urls = [line.strip() for line in lines if line.strip()]

# Download each file with curl
for url in file_urls:
    filename = url.split("/")[-1]
    filepath = os.path.join(download_dir, filename)

    if os.path.exists(filepath):
        log(f"✅ Already downloaded: {filename}")
        continue

    result = subprocess.run(
        ["curl", "-L", "-f", "--silent", "--show-error", "-o", filepath, url],
        capture_output=True
    )

    if result.returncode == 0:
        size = os.path.getsize(filepath)
        if size < 10240:  # <10KB
            log(f"⚠️  Warning: {filename} is too small ({size} bytes), possibly a bad download")
        else:
            log(f"✅ Downloaded: {filename} ({size / 1_048_576:.2f} MB)")
    else:
        log(f"❌ Failed: {filename}\n{result.stderr.decode().strip()}")

    # break  # Uncomment for single test download

# Report time
end_time = time.time()
duration = end_time - start_time
log(f"\n🕒 Start Time: {time.ctime(start_time)}")
log(f"🕒 End Time:   {time.ctime(end_time)}")
log(f"⏱️ Total Time: {timedelta(seconds=int(duration))} ({duration:.2f} seconds)")

log_file.close()
log(f"📁 Log saved to {log_file_path}")
