import os
import shutil

# Paths
episode_file = "SelectedEpisodes.TXT"
source_folder = "gdelt_ttxt_files"
destination_folder = "SelectedEpisodes"

# Create destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

# Step 1: Read episode URLs and extract episode IDs
with open(episode_file, 'r') as f:
    episode_urls = [line.strip() for line in f if line.strip()]
episode_ids = {url.split("/")[-1] for url in episode_urls}

# Step 2: List and filter matching .ttxt files
tar_files = [f for f in os.listdir(source_folder) if f.endswith(".ttxt")]
matching_files = [
    f for f in tar_files
    if any(f.startswith(episode_id) for episode_id in episode_ids)
]

# Step 3: Copy matching files to the destination folder
for f in matching_files:
    src_path = os.path.join(source_folder, f)
    dst_path = os.path.join(destination_folder, f)
    shutil.copy2(src_path, dst_path)

# Step 4: Print summary
print(f"Copied {len(matching_files)} files to '{destination_folder}' folder:")
for f in matching_files:
    print(f"- {f}")
