import os
import base64
import json
import requests
import csv
import time
import re

# CONFIGURATION
image_folder = 'all'
output_csv = 'gemini2flashexp_results.csv'
api_key = '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'  # Replace with your OpenRouter API key
sleep_time = 300  # in seconds

# Prompt
analysis_prompt = """Analyze the provided image for any indications of social media references and answer the following questions clearly and concisely:
1. Social Media Mention: Does the image suggest a mention of social media? (Answer: "Yes" or "No")
2. Platform Identification: If there is a mention, specify the platform(s) (e.g., Twitter, Facebook, Instagram). If multiple platforms are referenced, list their names. If it’s a general mention of social media without specifying a platform, respond with: "General Mention"
3. Mention Type: What kind of social media mention is this? Choose one or more from: Primary Topic, Supporting Evidence, Call to Action (such as asking to follow on social media, engage with program), Platform Discussion (discussing the social media platform), General Mention, Passing/Humorous Reference.
4. Social Media Logo: Is there a recognizable social media logo present in the image? (Answer: "Yes" or "No")
5. Social Media Logo Type: If a logo is present, specify which platform's logo it is (e.g., Twitter, Instagram, Facebook).
6. Social Media Post Screenshot: Does the image contain a screenshot of a social media post? (Answer: "Yes" or "No")
7. Social Media Screenshot Type: If a screenshot is present, what platform is it from? Provide the name of the platform (e.g., Twitter, Instagram, Facebook).
8. Post Context: If there is a social media post visible, describe its content or context. For example, does it show a reaction, opinion, news update, announcement, trend, humor, or something else? Provide a brief summary of what the post conveys.
9. Profile Mention: Is a specific social media profile or username referenced in the image? If yes, provide the username or profile name."""

csv_header = [
    'filename',
    'Social Media Mention',
    'Platform Identification',
    'Mention Type',
    'Social Media Logo',
    'Social Media Logo Type',
    'Social Media Post Screenshot',
    'Social Media Screenshot Type',
    'Post Context',
    'Profile Mention'
]

# Load already processed files (except ones with 429 or Exception)
existing_data = {}
if os.path.exists(output_csv):
    with open(output_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # if row['Social Media Mention'].startswith("ERROR 429") or row['Social Media Mention'].startswith("Exception"):
            #     continue  # allow retry
            existing_data[row['filename']] = True  # mark as processed

# Function to parse response
def parse_response(text):
    fields = [''] * 9
    match = re.findall(r'\d+\.\s*(.+?):\s*(.*?)(?=\n\d+\.|\Z)', text, re.DOTALL)
    mapping = {
        'Social Media Mention': 0,
        'Platform Identification': 1,
        'Mention Type': 2,
        'Social Media Logo': 3,
        'Social Media Logo Type': 4,
        'Social Media Post Screenshot': 5,
        'Social Media Screenshot Type': 6,
        'Post Context': 7,
        'Profile Mention': 8
    }
    for question, answer in match:
        question = question.strip()
        idx = mapping.get(question)
        if idx is not None:
            fields[idx] = answer.strip().replace('\n', ' ')
    return fields

# Append mode
with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if os.stat(output_csv).st_size == 0:
        writer.writerow(csv_header)

    for filename in sorted(os.listdir(image_folder)):
        if not filename.lower().endswith('.jpg'):
            continue
        if filename in existing_data:
            print(f"Skipping {filename}, already processed.")
            continue

        image_path = os.path.join(image_folder, filename)
        print(f"Processing {filename}")

        # Encode image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Retry logic
        while True:
            try:
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": analysis_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                            ]
                        }
                    ]
                }

                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    data=json.dumps(payload)
                )

                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    parsed_fields = parse_response(content)
                    break  # Success, exit retry loop
                elif response.status_code == 429:
                    print(f"⚠️ Rate limit hit for {filename}. Waiting {sleep_time * 3} seconds before retry...")
                    time.sleep(sleep_time * 3)
                else:
                    parsed_fields = [f"ERROR {response.status_code}: {response.text}"] + [''] * 8
                    break  # Exit retry loop on other errors

            except Exception as e:
                print(f"⚠️ Exception for {filename}: {e}")
                parsed_fields = [f"Exception: {e}"] + [''] * 8
                break  # Exit retry loop

        # Write result
        writer.writerow([filename] + parsed_fields)
        file.flush()

        print(f"✅ Finished {filename}, sleeping {sleep_time}s...\n")
        time.sleep(sleep_time)

print("🎉 All retries complete.")