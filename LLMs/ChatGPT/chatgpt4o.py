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

# time.sleep(3 * 60 * 60)  # Delay for 3 hours before any processing begins

# CONFIGURATION
image_folder = '../gemini2.5pro/FOXNEWSW_20200314_030000_Fox_News_at_Night_With_Shannon_Bream'
# image_folder = 'test'
output_csv = 'chatgpt_4o_results_run9.csv' 
log_file = 'chatgpt_4o_processing_log_run9.txt' 
api_key = '' # Replace with your OpenAI API key

long_pause_on_quota_exceeded = 300 # Pause for 5 mins if max retries for 429 are hit 


client = OpenAI(
    api_key=api_key,
    timeout=httpx.Timeout(30.0, write=5.0, connect=5.0, read=30.0), # Example timeout config
    max_retries=5 # OpenAI client's internal retries for transient errors including 429
)
CHATGPT_MODEL = "gpt-4o" # or "gpt-4-turbo", "gpt-4o-mini"

# Logging
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

log("🔄 ChatGPT 4o Script started.")

# Prompt
analysis_prompt =  """Analyze the provided image (of a TV screen) for any signs of social media references and answer the following questions clearly and concisely. Consider both textual and visual elements. Be specific about platform names, logos, and types of mentions.

Supported Platforms to Consider (not exhaustive): Twitter (bird logo), X (X logo), Facebook, Instagram, Threads, TikTok, YouTube, Truth Social, Parler, Rumble, Snapchat, LinkedIn, Discord, Pinterest

If a general mention of “social media” is made without naming a specific platform, indicate that as “General Mention.”

Questions:

1. Social Media Mention:
   Does the image include any reference to social media (either by name, logo, post, or textual mention)? Answer: “Yes” or “No”   
   If the answer is “No”, answer to all the other questions are “N/A”

2. Platform Identification:
   If yes, list all platforms that are mentioned or represented.
   - Use full names (e.g., Twitter, X, Instagram, Truth Social, etc.)
   - If no specific platform is named, but there’s a general reference to social media, answer: “No Platform”

3. Mention Type:
   What kind of reference is it? Select only one of the following:
   - Primary Topic (the social media mention is the primary topic)
   - Supporting Evidence (the social media mention is there to provide supporting evidence to a different story)
   - Call to Action (asking users to engage with the program e.g., "Follow us", "Share your story")
   - Platform Discussion (talking about or analyzing the social media platform itself)
   - General Mention (non-specific or background reference)
   - Passing/Humorous Reference (social media mentioned as a passing comment or humorous reference)

4. Social Media Logo:
   Is a recognizable logo from any social media platform visible in the image? Use only official, recognizable logos of known social media platforms.
   (Answer: “Yes” or “No” only)

5. Social Media Logo Type:
If the image contains one or more social media platform logos, specify which platform(s) they belong to. Only include official logos of known social media platforms (e.g., Twitter, Facebook, Instagram, TikTok, YouTube, Snapchat, LinkedIn, etc.). Do not include random shapes, text, or boxes that may resemble logos. Do not get confused with other logos that may be found on a TV screen. Do not get confused with @ symbol or logo of the channel (FOX NEWS, MSNBC, or CNN) as a social media mention. 
For Twitter-related logos, use the following labels: “Twitter (bird logo)” for the blue bird and  “X (X logo)” for the black/white “X” logo. 

Include all visible logos, even if they are: Partial (cut off or obscured) or Stylized (slightly altered but still clearly recognizable as an official social media logo)

6. Social Media Post Screenshot:
   Does the image include a screenshot of a post from a social media platform?
   (Answer: “Yes” or “No”)

7. Social Media Screenshot Type:
   If a screenshot is present, identify the platform it is from (e.g., Instagram, Twitter, Truth Social, etc.), Otherwise, “N/A”

8. Post Context:
   If there is a social media post visible, describe its content or context.
   For example, does it show a reaction, opinion, news update, announcement, trend, humor, or something else?
   Provide a brief summary of what the post conveys. Otherwise, “N/A”

9. Profile Mention:
   Is a specific social media username or profile referenced?
   - If yes, provide the username or profile name as displayed.
   - If not, “N/A”
"""


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

# Load already processed files
existing_data = {}
if os.path.exists(output_csv):
    with open(output_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Ensure the header matches for existing data check
        if reader.fieldnames == csv_header:
            for row in reader:
                existing_data[row['filename']] = True
        else:
            log(f"⚠️ Warning: CSV header mismatch. Existing data might not be correctly recognized.")

# Parse response
def parse_response(text):
    fields = [''] * 9
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

    # Normalize the prompt text for easier matching, remove bolding if any
    text = text.replace("**", "").strip()

    # Regex to find "N. Question Name: Answer" patterns
    patterns = {
        'Social Media Mention': r'1\.\s*Social Media Mention:\s*(.*?)(?=\n[2-9]\.|\Z)',
        'Platform Identification': r'2\.\s*Platform Identification:\s*(.*?)(?=\n[3-9]\.|\Z)',
        'Mention Type': r'3\.\s*Mention Type:\s*(.*?)(?=\n[4-9]\.|\Z)',
        'Social Media Logo': r'4\.\s*Social Media Logo:\s*(.*?)(?=\n[5-9]\.|\Z)',
        'Social Media Logo Type': r'5\.\s*Social Media Logo Type:\s*(.*?)(?=\n[6-9]\.|\Z)',
        'Social Media Post Screenshot': r'6\.\s*Social Media Post Screenshot:\s*(.*?)(?=\n[7-9]\.|\Z)',
        'Social Media Screenshot Type': r'7\.\s*Social Media Screenshot Type:\s*(.*?)(?=\n[8-9]\.|\Z)',
        'Post Context': r'8\.\s*Post Context:\s*(.*?)(?=\n9\.|\Z)',
        'Profile Mention': r'9\.\s*Profile Mention:\s*(.*?)(?=\n\d+\.|\Z)' # Catches up to next number or end
    }

    for question_name, index in mapping.items():
        pattern = patterns.get(question_name)
        if pattern:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE) 
            if match:
                answer = match.group(1).strip()
                if question_name != 'Social Media Mention' and fields[0].lower() == 'no':
                    fields[index] = 'N/A'
                else:
                    fields[index] = answer.replace('\n', ' ')
            else:
                if question_name == 'Social Media Mention':
                    fields[index] = 'Could not parse' 
                elif fields[0].lower() == 'no': 
                    fields[index] = 'N/A'
                else:
                    fields[index] = 'N/A' 
    return fields


# Process images
with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if os.stat(output_csv).st_size == 0:
        writer.writerow(csv_header)

    for filename in sorted(os.listdir(image_folder)):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')): # Added more image types
            continue
        # Ensure the filename matches how it's stored in the CSV
        csv_filename_check = f"{image_folder}-{filename}"
        if csv_filename_check in existing_data:
            log(f"⏩ Skipping {filename}, already processed.")
            continue

        image_path = os.path.join(image_folder, filename)
        log(f"📸 Processing {filename}")

        attempt_count_for_quota = 0 # To track how many times we've hit a 429 *after* internal retries
        
        while attempt_count_for_quota < 1: # Only one "long pause" attempt for now after max_retries failed
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

                # OpenAI's client handles retries for RateLimitError internally based on client.max_retries
                response = client.chat.completions.create(
                    model=CHATGPT_MODEL,
                    messages=messages,
                    max_tokens=1000, # Set a reasonable max_tokens for response length
                    temperature=0.2
                )
                
                content = response.choices[0].message.content
                parsed_fields = parse_response(content)
                successful_request = True
                break # If successful, exit the outer retry loop

            except openai.RateLimitError as e:
                # This block is for when OpenAI's *internal* retries for 429 have been exhausted.
                # It indicates a more persistent rate limit issue.
                attempt_count_for_quota += 1
                log(f"❌ Persistent RateLimitError for {filename} after client's internal retries. Error: {e}")
                log(f"Pausing for {long_pause_on_quota_exceeded} seconds before attempting to process further images.")
                time.sleep(long_pause_on_quota_exceeded)
                parsed_fields = [f"Quota Exceeded (OpenAI)"] + [''] * 8 # Mark as failed
                successful_request = False
                break # Break from outer loop for this image, then move to next image

            except openai.APIStatusError as e:
                # Catch other OpenAI API errors (e.g., 400 Bad Request, 500 Server Error)
                log(f"❌ OpenAI API Status Error for {filename}: Status {e.status_code}, Message: {e.response.text}. Skipping image.")
                parsed_fields = [f"API Error ({e.status_code})"] + [''] * 8
                successful_request = False
                break # Don't retry these, usually indicate a problem with the request itself

            except openai.APIConnectionError as e:
                # Catch network-related errors
                log(f"❌ OpenAI API Connection Error for {filename}: {e}. Retrying in 10 seconds.")
                time.sleep(10) # Simple retry for connection errors
                attempt_count_for_quota += 1 # Treat as an attempt for persistent network issues
                if attempt_count_for_quota >= 3: # Limit retries for connection errors too
                    log(f"❌ Repeated Connection Errors for {filename}. Skipping image.")
                    parsed_fields = [f"Connection Error"] + [''] * 8
                    successful_request = False
                    break
                continue # Retry the current image for connection errors

            except Exception as e:
                log(f"❌ Unexpected Exception for {filename}: {e}. Stopping script.")
                exit()
        
        filename_with_folder = f"{image_folder}-{filename}"
        writer.writerow([filename_with_folder] + parsed_fields) # Always write a row, even if failed
        
        if successful_request:
            log(f"✅ Finished {filename}, next image after a short break.\n")
        else:
            log(f"❗ Failed to process {filename} due to previous errors, logged status to CSV.")

        file.flush() # Ensure data is written to disk after each image

log("🏁 ChatGPT 4o Script finished.")