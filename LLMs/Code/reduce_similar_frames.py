import os
import tarfile
import tempfile
from PIL import Image
import imagehash
import shutil
import sys
import time

# Paths
channel = sys.argv[1]

input_base =  f"/home/hjaya002/LLMS/image_data/{channel}"
output_base =  f"/home/hjaya002/LLMS/reduced_image_data_t3/{channel}"
# input_base = "/home/hjaya002/LLMS/test_image_data/CNN"
# output_base = "/home/hjaya002/LLMS/test_reduced_image_data/CNN"

# Parameters
hash_size = 8
threshold = 3  # Hamming distance for similarity

def get_frame_number(filename):
    """Extract numeric frame index from filename (without extension)."""
    return int(os.path.splitext(filename)[0])

def process_folder(input_folder, output_folder):
    """Run the image grouping process for a single folder of images."""
    os.makedirs(output_folder, exist_ok=True)

    image_files = sorted(
        [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
        key=get_frame_number
    )

    last_hash = None
    current_group = []

    for filename in image_files:
        filepath = os.path.join(input_folder, filename)
        image = Image.open(filepath)
        current_hash = imagehash.average_hash(image, hash_size=hash_size)

        if last_hash is None or last_hash - current_hash > threshold:
            if current_group:
                # Save middle image of the group
                middle_index = len(current_group) // 2
                src_file = os.path.join(input_folder, f"{current_group[middle_index]}.jpg")
                output_name = f"{current_group[0]}-{current_group[-1]}.jpg" if len(current_group) > 1 else f"{current_group[0]}.jpg"
                dst_file = os.path.join(output_folder, output_name)
                shutil.copy2(src_file, dst_file)
            current_group = [os.path.splitext(filename)[0]]
        else:
            current_group.append(os.path.splitext(filename)[0])

        last_hash = current_hash

    # Handle final group
    if current_group:
        middle_index = len(current_group) // 2
        src_file = os.path.join(input_folder, f"{current_group[middle_index]}.jpg")
        output_name = f"{current_group[0]}-{current_group[-1]}.jpg" if len(current_group) > 1 else f"{current_group[0]}.jpg"
        dst_file = os.path.join(output_folder, output_name)
        shutil.copy2(src_file, dst_file)

def main():    
    print(f"Start processing channel: {channel}")
    start_time = time.time()
    for tar_filename in os.listdir(input_base):
        if tar_filename.lower().endswith(".tar"):
            tar_path = os.path.join(input_base, tar_filename)
            folder_name = tar_filename.split(".frames1fps")[0]  # strip .frames1fps.tar
            # output_folder = os.path.join(output_base, output_name)
            # print(folder_name)
            print(f"Processing {tar_filename}...")

            with tempfile.TemporaryDirectory() as tmp_dir:
                # Extract tar file
                with tarfile.open(tar_path, "r") as tar:
                    tar.extractall(path=tmp_dir)
                # print(tmp_dir)
                extracted_folder = os.path.join(tmp_dir, folder_name)
                # print(extracted_folder)
                
                # Process extracted images
                output_folder = os.path.join(output_base, folder_name)
                process_folder(extracted_folder, output_folder)

                print(f"✅ Finished: {folder_name}")
    end_time = time.time()
    elapsed = end_time - start_time
    print("=======================================")
    print(f"Finished processing channel: {channel}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"End time:   {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print("=======================================")

if __name__ == "__main__":
    main()
