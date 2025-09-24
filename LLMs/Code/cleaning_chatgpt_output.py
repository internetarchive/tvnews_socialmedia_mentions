import pandas as pd
import re

input_filename = "chatgpt40_CNN_t3_v4.csv"

chatgpt_df = pd.read_csv(input_filename, keep_default_na=False)
# chatgpt_df['filename'] = chatgpt_df['filename'].str.replace("/home/hjaya002/LLMS/test_reduced_image_data/CNN/", "", regex=False).str.strip()
chatgpt_df['filename'] = chatgpt_df['filename'].str.replace("/home/hjaya002/LLMS/reduced_image_data_t3_blackframesremoved/CNN", "", regex=False).str.strip()

# def strip_answer(df):

def clean_binary_column(df, column_name):
    df[column_name] = df[column_name].replace(['N/A', '- N/A', '- Answer: No','Answer: N/A', '- Answer: N/A'], 'No')
    df[column_name] = df[column_name].replace(['- Answer: Yes','Answer: Yes',], 'Yes')
    # chatgpt_df['Social Media Logo'] = chatgpt_df['Social Media Logo'].replace(, 'No')

    # Check for unexpected values
    cleaned_logo_col = df[column_name].astype(str).str.strip().str.lower()
    unexpected_values = cleaned_logo_col[~cleaned_logo_col.isin(['yes', 'no'])].unique()

    # print(f"Unexpected (lowercased) values in {column_name}:", unexpected_values)
    # unexpected_rows = cleaned_logo_col[unexpected_values]
    # print("Row:", unexpected_rows)
    return df

chatgpt_df1 = clean_binary_column(chatgpt_df, 'Social Media Logo')
chatgpt_df2 = clean_binary_column(chatgpt_df1, 'Social Media Post Screenshot')


def replace_exact_x(value):
    if pd.isna(value):
        return value
    if "Twitter (X)" in value:
        return value
    return re.sub(r'\bX\b', 'Twitter (X)', value)

def check_twitter_instances(value):
    if pd.isna(value):
        return value

    original = str(value).strip()
    lower_val = original.lower()

    has_twitter = "twitter (bird logo)" in lower_val
    has_x = (
        "x (x logo)" in lower_val
        or "twitter (x logo)" in lower_val
        or re.search(r'\bX\b', original)  # match exact standalone X
    )

    if has_twitter:
        original = original.replace("Twitter (bird logo)", "Twitter")
    if has_x:
        original = original.replace("X (X logo)", "Twitter (X)")
        original = original.replace("Twitter (X logo)", "Twitter (X)")
        original = replace_exact_x(original)

    return original

def check_otherplatform_instances(value):
    original = str(value).strip()
    # original = original.replace("N/A", "")
    original = original.replace("- N/A", "N/A")
    original = original.replace("Facebook (stylized)", "Facebook")
    return original
    

chatgpt_df2['Social Media Logo Type'] = chatgpt_df2['Social Media Logo Type'].apply(check_twitter_instances)
chatgpt_df2['Social Media Logo Type'] = chatgpt_df2['Social Media Logo Type'].apply(check_otherplatform_instances)

# print(chatgpt_df2['Social Media Logo Type'].unique())

chatgpt_df2['Social Media Screenshot Type'] = chatgpt_df2['Social Media Screenshot Type'].apply(check_twitter_instances)
chatgpt_df2['Social Media Screenshot Type'] = chatgpt_df2['Social Media Screenshot Type'].apply(check_otherplatform_instances)

# print(chatgpt_df2['Social Media Screenshot Type'].unique())
# chatgpt_df2.rename(columns={'Social Media Screenshot Type': 'Social Media Post Screenshot Type'}, inplace=True)

output_filename = f"cleaned/{input_filename[:-4]}_cleaned.csv"
chatgpt_df2.to_csv(output_filename, index=False)
