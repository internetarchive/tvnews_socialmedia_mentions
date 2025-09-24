import os
import base64
import json
import csv
import time
import re
import datetime
import openai
from openai import OpenAI
import httpx
import tarfile
import tempfile
import shutil
import cv2

script_start_time = datetime.datetime.now()
print(f"Script started at: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# /home/hjaya002/LLMS/image_data/CNN
# CONFIGURATION
main_image_root = '/home/hjaya002/LLMS/reduced_image_data_t3_blackframesremoved/CNN'
api_key = 'xyz'  # OpenAI API key

long_pause_on_quota_exceeded = 300  # 5 mins pause on quota hit
CHATGPT_MODEL = "gpt-4o"

# Initialize OpenAI client once, reuse for all
client = OpenAI(
    api_key=api_key,
    timeout=httpx.Timeout(30.0, write=5.0, connect=5.0, read=30.0),
    max_retries=5
)

analysis_prompt = """Instructions: Analyze the image carefully and answer the following questions. Be strict and conservative in identifying logos or screenshots. Only mark “Yes” if you are confident based on visual elements, not text alone. Be specific about platform names, logos, and types of mentions.

Only the following platforms are valid for detection (no others): 'Facebook', 'Instagram', ‘Twitter (bird logo)’, 'X (X logo)', 'Threads', 'TikTok', 'Truth Social', 'LinkedIn', 'Meta', 'Parler', 'Pinterest', 'Rumble', 'Snapchat', 'YouTube', 'Discord'. 

Do NOT consider any other platforms (e.g., messaging apps like WhatsApp, Messenger, Skype) as social media platforms for this task.

Questions:

1. Social Media Logo:
Is a recognizable logo from any social media platform visible in the image? Only detect official logos of above mentioned social media platforms. The platform name as text on the provided image is NOT a logo. Only detect the official graphical logo. Do not include random shapes, text, or boxes that may resemble logos. If any element partially resembles a logo or is ambiguous, mark as ‘No’. Only mark ‘Yes’ if the logo is clearly identifiable. Ensure the colors match the official logo. Do not label an object as a platform logo based on shape alone unless colors and design are correct. In grayscale images, consider contrast and shape carefully. Do not count icons, buttons, or interface hints (e.g., Instagram heart button, Facebook like button) as the official platform logo. Do not get confused with other logos that may be found on a TV screen. Do not get confused with @ symbol or logo of the channel (FOX NEWS, MSNBC, or CNN) as a social media mention. 

X Logo Rules (strict):  
- Only mark “Yes” for the exact stylized ‘X’ logo of the platform.  
- Do NOT get confused by the Xfinity logo which is asymmetric with one arm of X extended. It is NOT the X logo we are interested in.
- Random X letters, X in “FOX”  on the Fox News logo, or other brands like Xfinity logo are also NOT "X" logo.
- The logo must have the correct sharp design and proportions. If unsure, always answer “No.”
  
(Answer: “Yes” or “No” only)

2. Logo Detection Confidence:
Provide a confidence score between 0 and 1 for your answer in Question 1.
- If answer to Question 1 is “Yes”: the confidence score reflects how certain you are that it’s a social media platform logo in the given image.
- If answer to Question 1 is “No”: the confidence score reflects how certain you are that there is no social media platform logo in the given image.
Only provide a number, no extra text. Do not answer as “N/A”.

3. Social Media Logo Type:
If the answer to question 1 is “Yes”, specify which platform(s) they belong to. Do not say “N/A”. For Twitter-related logos, use the following labels: “Twitter (bird logo)” if it’s the bird logo and  “X (X logo)” for the black/white “X” logo. If the answer to question 1 is “No”, answer is “N/A” only.

4. Social Media Post Screenshot:
Does the provided image include a screenshot of a user post from one of the listed social media platforms? A user post screenshot is an image within the provided image that directly captures a social media post made by a platform user (e.g., a Facebook post, tweet on Twitter/X, Instagram post). Do not count screenshots of the platform interface, buttons, menus, or other content that is not an actual user post. Features such as usernames/handles, profile pictures, timestamps, reactions, likes, or platform layout elements can be clues but do not alone guarantee a post screenshot. Simply having the word “post” on screen does not count. Only mark “Yes” if there is clear evidence; do not guess ordinary photos, text, or graphics as posts.
(Answer: “Yes” or “No” only)

5. Screenshot Detection Confidence:
Provide a confidence score between 0 and 1 for your answer in Question 1.
- If answer to Question 1 is “Yes”: the confidence score reflects how certain you are that it’s a social media post screenshot in the given image.
- If answer to Question 1 is “No”: the confidence score reflects how certain you are that there is no social media post screenshot in the given image.
Only provide a number, no extra text. Do not answer as “N/A”.

4. Social Media Screenshot Type:
   If the answer to question 4 is “Yes”,  identify the platform it is from (e.g., Instagram, Twitter, Truth Social, etc.). Do not say “N/A”. If the answer to question 3 is “No”, answer “N/A” only. """



# Updated CSV header with confidence fields
csv_header = [
    'filename',
    'Social Media Logo',
    'Logo Detection Confidence',
    'Social Media Logo Type',
    'Social Media Post Screenshot',
    'Screenshot Detection Confidence',
    'Social Media Screenshot Type'
]

def log(message, log_file):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def parse_response(text):
    """
    Parses the model response and returns all 6 fields:
    0: Social Media Logo
    1: Logo Detection Confidence
    2: Social Media Logo Type
    3: Social Media Post Screenshot
    4: Screenshot Detection Confidence
    5: Social Media Screenshot Type
    """
    # Initialize fields
    fields = [''] * 6

    mapping = {
        'Social Media Logo': 0,
        'Logo Detection Confidence': 1,
        'Social Media Logo Type': 2,
        'Social Media Post Screenshot': 3,
        'Screenshot Detection Confidence': 4,
        'Social Media Screenshot Type': 5
    }

    # Clean up text
    text = text.replace("**", "").strip()

    # Flexible regex: look for next numbered question OR end of text
    patterns = {
        'Social Media Logo': r'1\.\s*Social Media Logo:\s*(.*?)(?=\n\d+\.|\Z)',
        'Logo Detection Confidence': r'2\.\s*Logo Detection Confidence:\s*(.*?)(?=\n\d+\.|\Z)',
        'Social Media Logo Type': r'3\.\s*Social Media Logo Type:\s*(.*?)(?=\n\d+\.|\Z)',
        'Social Media Post Screenshot': r'4\.\s*Social Media Post Screenshot:\s*(.*?)(?=\n\d+\.|\Z)',
        'Screenshot Detection Confidence': r'5\.\s*Screenshot Detection Confidence:\s*(.*?)(?=\n\d+\.|\Z)',
        'Social Media Screenshot Type': r'6\.\s*Social Media Screenshot Type:\s*(.*?)(?=\Z)'
    }

    for question_name, index in mapping.items():
        pattern = patterns.get(question_name)
        if pattern:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                answer = match.group(1).strip()

                # If field is a confidence, extract numeric 0-1 if possible
                if question_name in ['Logo Detection Confidence', 'Screenshot Detection Confidence']:
                    num_match = re.search(r'0*(1(?:\.0+)?|0?\.\d+)', answer)
                    if num_match:
                        answer = num_match.group(1)
                    else:
                        answer = "N/A"

                # Apply dependent logic for N/A
                if index in [1, 2] and fields[0].lower() != "yes":
                    fields[index] = "N/A"
                elif index in [4, 5] and fields[3].lower() != "yes":
                    fields[index] = "N/A"
                else:
                    fields[index] = answer.replace('\n', ' ')
            else:
                # Default N/A if not matched
                if index in [1, 2] and fields[0].lower() != "yes":
                    fields[index] = "N/A"
                elif index in [4, 5] and fields[3].lower() != "yes":
                    fields[index] = "N/A"
                else:
                    fields[index] = "N/A"

    return fields


def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    output_csv = f"{folder_name}.csv"
    log_file = f"{folder_name}_log.txt"

    log(f"Processing folder: {folder_name}", log_file)

    # Load already processed files for this folder
    existing_data = {}
    if os.path.exists(output_csv):
        with open(output_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames == csv_header:
                for row in reader:
                    existing_data[row['filename']] = True
            else:
                log(f"Warning: CSV header mismatch. Existing data might not be recognized.", log_file)

    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(output_csv).st_size == 0:
            writer.writerow(csv_header)

        for filename in sorted(os.listdir(folder_path)):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                continue

            # Construct consistent filename key (folder-filename)
            filename_with_folder = f"{folder_path}-{filename}"
            if filename_with_folder in existing_data:
                log(f"Skipping {filename}, already processed.", log_file)
                continue

            image_path = os.path.join(folder_path, filename)
            log(f"Processing {filename}", log_file)

            attempt_count_for_quota = 0
            successful_request = False

            while attempt_count_for_quota < 1:
                try:
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": analysis_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                            ]
                        }
                    ]

                    response = client.chat.completions.create(
                        model=CHATGPT_MODEL,
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.0
                    )

                    content = response.choices[0].message.content
                    
#                     # Quick parse to check if either main answer is "Yes"
#                     logo_yes = re.search(r'1\.\s*Social Media Logo:\s*Yes', content, re.IGNORECASE)
                    
#                     if logo_yes:
#                         print(f"Model output for {filename} (Yes detected):")
#                         print("----- Model Output Start -----")
#                         print(content)
#                         print("----- Model Output End -----")

                    parsed_fields = parse_response(content)
                    successful_request = True
                    break

                except openai.RateLimitError as e:
                    attempt_count_for_quota += 1
                    log(f"Persistent RateLimitError for {filename} after retries. Error: {e}", log_file)
                    log(f"Pausing for {long_pause_on_quota_exceeded} seconds.", log_file)
                    time.sleep(long_pause_on_quota_exceeded)
                    parsed_fields = [f"Quota Exceeded (OpenAI)"] + [''] * 3
                    successful_request = False
                    break

                except openai.APIStatusError as e:
                    log(f"API Status Error for {filename}: {e.status_code}, {e.response.text}. Skipping.", log_file)
                    parsed_fields = [f"API Error ({e.status_code})"] + [''] * 3
                    successful_request = False
                    break

                except openai.APIConnectionError as e:
                    log(f"API Connection Error for {filename}: {e}. Retrying in 10 seconds.", log_file)
                    time.sleep(10)
                    attempt_count_for_quota += 1
                    if attempt_count_for_quota >= 3:
                        log(f"Repeated Connection Errors for {filename}. Skipping.", log_file)
                        parsed_fields = [f"Connection Error"] + [''] * 3
                        successful_request = False
                        break
                    continue

                except Exception as e:
                    log(f"Unexpected Exception for {filename}: {e}. Stopping.", log_file)
                    exit()

            writer.writerow([filename_with_folder] + parsed_fields)
            file.flush()

            if successful_request:
                log(f"Finished {filename}\n", log_file)
            else:
                log(f"Failed to process {filename} due to errors.", log_file)

    log(f"🏁 Finished folder: {folder_name}\n", log_file)


# Main loop: process each folder in main_image_root
# for folder in sorted(os.listdir(main_image_root)):
#     # print("hello")
#     folder_path = os.path.join(main_image_root, folder)
#     if os.path.isdir(folder_path):
#         print(folder_path)
#         process_folder(folder_path)

# Main loop: process each folder or .tar file in main_image_root
for entry in sorted(os.listdir(main_image_root)):
    entry_path = os.path.join(main_image_root, entry)

    if os.path.isdir(entry_path):
        # Normal folder
        print(f"Processing folder: {entry_path}")
        process_folder(entry_path)

    elif entry.endswith(".tar"):
        # Extract .tar into a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Extracting {entry_path} to {tmpdir}")
            with tarfile.open(entry_path, "r") as tar:
                tar.extractall(path=tmpdir)

            # Assume tar contains a single root folder; get its path
            extracted_items = os.listdir(tmpdir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(tmpdir, extracted_items[0])):
                extracted_folder = os.path.join(tmpdir, extracted_items[0])
            else:
                # If multiple items, treat tmpdir itself as the folder
                extracted_folder = tmpdir

            print(f"Processing extracted folder: {extracted_folder}")
            process_folder(extracted_folder)

# At the very end, after the main loop that processes all folders:
script_end_time = datetime.datetime.now()
print(f"Script finished at: {script_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
duration = script_end_time - script_start_time
print(f"Total runtime: {duration}")

with open("overall_processing_log.txt", "a", encoding="utf-8") as f:
    f.write(f"Script started at: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Script finished at: {script_end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total runtime: {duration}\n\n")
