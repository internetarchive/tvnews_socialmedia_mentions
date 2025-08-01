import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# Load the CSV files
gold_df = pd.read_csv("gold_standard_images_foxnews_shannon.csv")
chatgpt_df = pd.read_csv("chatgpt_4o_results_run6.csv")

# Normalize filenames
chatgpt_df['filename'] = chatgpt_df['filename'].str.replace("../gemini2.5pro/", "", regex=False).str.strip()
gold_df['filename'] = gold_df['filename'].str.strip()

# Evaluation function
def evaluate_detection(gold_column, chatgpt_column, prefix):
    # Ground truth
    gold_labels = gold_df[gold_column].fillna('').str.lower() == 'yes'
    gold_map = dict(zip(gold_df['filename'], gold_labels))
    chatgpt_df[f'{prefix}_true'] = chatgpt_df['filename'].apply(lambda x: gold_map.get(x, False))

    # Prediction
    chatgpt_df[f'{prefix}_pred'] = chatgpt_df[chatgpt_column].fillna('').str.lower() == 'yes'

    # FP and FN
    chatgpt_df[f'{prefix}_fp'] = (chatgpt_df[f'{prefix}_pred'] == True) & (chatgpt_df[f'{prefix}_true'] == False)
    chatgpt_df[f'{prefix}_fn'] = (chatgpt_df[f'{prefix}_pred'] == False) & (chatgpt_df[f'{prefix}_true'] == True)

    # Metrics
    y_true = chatgpt_df[f'{prefix}_true']
    y_pred = chatgpt_df[f'{prefix}_pred']
    conf_matrix = confusion_matrix(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # Print metrics
    print(f"\n=== {prefix.upper()} Detection ===")
    print("Confusion Matrix:")
    print(conf_matrix)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

# Evaluate and print for logo
evaluate_detection("Social Media Logo", "Social Media Logo", "logo")

# Evaluate and print for screenshot
evaluate_detection("Social Media Screenshot", "Social Media Post Screenshot", "screenshot")

# Save verification file
output_cols = [
    'filename',
    'logo_true', 'logo_pred', 'logo_fp', 'logo_fn',
    'screenshot_true', 'screenshot_pred', 'screenshot_fp', 'screenshot_fn'
]
chatgpt_df[output_cols].to_csv("logo_screenshot_verification_with_fp_fn.csv", index=False)
print("\n✅ Saved: logo_screenshot_verification_with_fp_fn.csv")


# import pandas as pd
# from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# # Load the CSV files
# gold_df = pd.read_csv("gold_standard_images_foxnews_shannon.csv")
# chatgpt_df = pd.read_csv("chatgpt_4o_results.csv")

# # Normalize filenames
# chatgpt_df['filename'] = chatgpt_df['filename'].str.replace("../gemini2.5pro/", "", regex=False).str.strip()
# gold_df['filename'] = gold_df['filename'].str.strip()

# # Define evaluation function
# def evaluate_detection(gold_column, chatgpt_column):
#     # Create binary labels from gold standard and ChatGPT columns
#     gold_labels = gold_df[gold_column].fillna('').str.lower() == 'yes'
#     gold_map = dict(zip(gold_df['filename'], gold_labels))

#     chatgpt_preds = chatgpt_df[chatgpt_column].fillna('').str.lower() == 'yes'
#     chatgpt_df['true_label_temp'] = chatgpt_df['filename'].apply(lambda x: gold_map.get(x, False))
#     chatgpt_df['predicted_label_temp'] = chatgpt_preds

#     y_true = chatgpt_df['true_label_temp']
#     y_pred = chatgpt_df['predicted_label_temp']

#     # Calculate metrics
#     conf_matrix = confusion_matrix(y_true, y_pred)
#     accuracy = accuracy_score(y_true, y_pred)
#     precision = precision_score(y_true, y_pred, zero_division=0)
#     recall = recall_score(y_true, y_pred, zero_division=0)
#     f1 = f1_score(y_true, y_pred, zero_division=0)

#     return conf_matrix, accuracy, precision, recall, f1

# # Evaluate for Logo
# logo_conf_matrix, logo_acc, logo_prec, logo_rec, logo_f1 = evaluate_detection(
#     "Social Media Logo", "Social Media Logo"
# )

# # Evaluate for Screenshot
# screenshot_conf_matrix, screenshot_acc, screenshot_prec, screenshot_rec, screenshot_f1 = evaluate_detection(
#     "Social Media Screenshot", "Social Media Post Screenshot"
# )

# # Print results
# print("=== Social Media Logo ===")
# print("Confusion Matrix:\n", logo_conf_matrix)
# print(f"Accuracy:  {logo_acc:.4f}")
# print(f"Precision: {logo_prec:.4f}")
# print(f"Recall:    {logo_rec:.4f}")
# print(f"F1 Score:  {logo_f1:.4f}\n")

# print("=== Social Media Screenshot ===")
# print("Confusion Matrix:\n", screenshot_conf_matrix)
# print(f"Accuracy:  {screenshot_acc:.4f}")
# print(f"Precision: {screenshot_prec:.4f}")
# print(f"Recall:    {screenshot_rec:.4f}")
# print(f"F1 Score:  {screenshot_f1:.4f}")
