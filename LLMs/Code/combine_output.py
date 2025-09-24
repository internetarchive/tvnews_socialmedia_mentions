import os
import csv

# Folder where the individual CSV files are stored 
csv_folder = '.' 

# Output combined CSV filename
combined_csv = 'chatgpt40_CNN_t3_v4.csv'

# chatgpt40_FOXNEWS_t3_v3.csv

csv_header = [
    'filename',
    'Social Media Logo',
    'Logo Detection Confidence',
    'Social Media Logo Type',
    'Social Media Post Screenshot',
    'Screenshot Detection Confidence',
    'Social Media Screenshot Type'
]

# Collect all CSV files matching the pattern 
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv') and f.startswith("CNNW_") and f != combined_csv]

with open(combined_csv, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(csv_header)  # Write header once

    for csv_file in sorted(csv_files):
        file_path = os.path.join(csv_folder, csv_file)
        with open(file_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Skip header of each individual file
            if header != csv_header:
                print(f"Warning: Header mismatch in {csv_file}")
            for row in reader:
                writer.writerow(row)

print(f"Combined {len(csv_files)} CSV files into '{combined_csv}'")
