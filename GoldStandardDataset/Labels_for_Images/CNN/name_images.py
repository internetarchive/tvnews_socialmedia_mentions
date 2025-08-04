import os
import shutil

# Root directory containing the CNN folders
root_dir = '.'  # Change if needed
output_dir = 'all'
os.makedirs(output_dir, exist_ok=True)

# Loop through all folders starting with FOXNEWSW
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)

    if not os.path.isdir(folder_path) or not folder_name.startswith('CNNW'):
        continue
    folder_basename = folder_name.split('.')[0]

    # Process each .jpg image inside the folder
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.jpg'):
            new_name = f"{folder_basename}-{file_name}"
            src = os.path.join(folder_path, file_name)
            dst = os.path.join(output_dir, new_name)
            shutil.copy2(src, dst)  # use shutil.move() if you want to remove originals

print("All CNNW images renamed and moved to 'all/' folder.")
