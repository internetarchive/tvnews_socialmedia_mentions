import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from sklearn.preprocessing import MultiLabelBinarizer

filename = "chatgpt_4o_results_run12_cleaned"

# chatgpt_4o_results_cleaned.csv
# chatgpt_4o_results_run2_cleaned.csv
# chatgpt_4o_results_run3_cleaned.csv
# chatgpt_4o_results_run4_cleaned.csv
# chatgpt_4o_results_run5_cleaned.csv
# chatgpt_4o_results_run6_cleaned.csv
# chatgpt_4o_results_run7_cleaned.csv


# Load CSVs
gold_df = pd.read_csv("gold_standard_images_foxnews_shannon.csv")
chatgpt_df = pd.read_csv(f"cleaned/{filename}.csv")

# Normalize filenames
# gold_df['filename'] = gold_df['filename'].str.strip()
# chatgpt_df['filename'] = chatgpt_df['filename'].str.replace("../gemini2.5pro/", "", regex=False).str.strip()

# Merge both with suffixes to distinguish columns
merged_df = pd.merge(
    chatgpt_df, gold_df, on="filename", how="left", suffixes=("_pred", "_gold")
)

# Fill missing gold labels with 'no' (i.e., not in gold = not present)
merged_df["Social Media Logo_gold"] = merged_df["Social Media Logo_gold"].fillna("no")
merged_df["Social Media Screenshot"] = merged_df["Social Media Screenshot"].fillna("no")

def to_bool_yes(value):
    """Convert 'yes' to True, everything else to False."""
    if isinstance(value, str):
        return value.strip().lower() == 'yes'
    return False


def binary_detection_eval(prefix, detect_col_pred, detect_col_gold):
    """Evaluate binary detection (yes/no)."""
    y_true = merged_df[detect_col_gold].apply(to_bool_yes)
    y_pred = merged_df[detect_col_pred].apply(to_bool_yes)

    merged_df[f'{prefix}_true'] = y_true
    merged_df[f'{prefix}_pred'] = y_pred
    merged_df[f'{prefix}_fp'] = y_pred & ~y_true
    merged_df[f'{prefix}_fn'] = ~y_pred & y_true

    cm = confusion_matrix(y_true.astype(int), y_pred.astype(int))

    # Unpack confusion matrix elements:
    tn, fp = cm[0,0], cm[0,1]
    fn, tp = cm[1,0], cm[1,1]

    print(f"\n=== {prefix.upper()} DETECTION (Binary yes/no) ===")

    # print("Confusion Matrix:\n")
    print(f"                Predicted: Yes    Predicted: No")
    print(f"Actual: Yes        {tp:5}            {fn:5}")
    print(f"Actual: No         {fp:5}           {tn:5}")

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    # print("Confusion Matrix:\n", cm)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")

# Run evaluations
logo_binary_results = binary_detection_eval("logo", "Social Media Logo_pred", "Social Media Logo_gold")
screenshot_binary_results = binary_detection_eval("screenshot", "Social Media Post Screenshot", "Social Media Screenshot")

#####LOGO#####

# Convert NaN to empty string, then split and strip
def parse_labels(cell):
    if isinstance(cell, str):
        return [label.strip() for label in cell.split(',') if label.strip()]
    return []

# Parse and prepare label lists
merged_df['logo_types_gold'] = merged_df['Social Media Logo Type_gold'].apply(parse_labels)
merged_df['logo_types_pred'] = merged_df['Social Media Logo Type_pred'].apply(parse_labels)

# Get all unique labels (from gold and predicted)
all_logo_labels = sorted(set().union(*merged_df['logo_types_gold']) | set().union(*merged_df['logo_types_pred']))

# Fit MLP on full label set
mlb = MultiLabelBinarizer(classes=all_logo_labels)
mlb.fit([all_logo_labels])  # Ensure full label space is registered
y_true_type = mlb.transform(merged_df['logo_types_gold'])
y_pred_type = mlb.transform(merged_df['logo_types_pred'])

print("\n=== Evaluation: Social Media Logo Types (multi-label classification) ===")
print("Labels:", mlb.classes_)

# print("Precision (macro):", precision_score(y_true_type, y_pred_type, average='macro', zero_division=0))
# print("Recall (macro):", recall_score(y_true_type, y_pred_type, average='macro', zero_division=0))
# print("F1-score (macro):", f1_score(y_true_type, y_pred_type, average='macro', zero_division=0))

report = classification_report(
    y_true_type,
    y_pred_type,
    target_names=mlb.classes_,
    labels=range(len(mlb.classes_)),
    output_dict=True,
    zero_division=0
)
# print("\nPer-label performance:\n", report)

# Warn on unexpected predicted-only labels
gold_labels = set().union(*merged_df['logo_types_gold'])
pred_labels = set().union(*merged_df['logo_types_pred'])
unexpected_predicted_labels = pred_labels - gold_labels
if unexpected_predicted_labels:
    print("⚠️ Predicted labels not found in gold standard:")
    print(unexpected_predicted_labels)
else:
    print("✅ All predicted labels appear in gold standard.")

# Convert to DataFrame
report_df = pd.DataFrame(report).transpose()
# Save to CSV
report_df.to_csv(f"logo_evaluation_report/{filename}_logoevaluation_report.csv", index=True)

#####Screenshot#####

# Apply parsing for screenshot labels
merged_df['screenshot_types_gold'] = merged_df['Social Media Screenshot Type_gold'].apply(parse_labels)
merged_df['screenshot_types_pred'] = merged_df['Social Media Screenshot Type_pred'].apply(parse_labels)

# Get all unique screenshot labels
all_screenshot_labels = sorted(set().union(*merged_df['screenshot_types_gold']) | set().union(*merged_df['screenshot_types_pred']))

# Fit MLP on combined label set
mlb_screenshot = MultiLabelBinarizer(classes=all_screenshot_labels)
mlb_screenshot.fit([all_screenshot_labels])
y_true_screenshot = mlb_screenshot.transform(merged_df['screenshot_types_gold'])
y_pred_screenshot = mlb_screenshot.transform(merged_df['screenshot_types_pred'])

# print("\n=== Evaluation: Social Media Screenshot Types (multi-label classification) ===")
# print("Labels:", mlb_screenshot.classes_)

# print("Precision (macro):", precision_score(y_true_screenshot, y_pred_screenshot, average='macro', zero_division=0))
# print("Recall (macro):", recall_score(y_true_screenshot, y_pred_screenshot, average='macro', zero_division=0))
# print("F1-score (macro):", f1_score(y_true_screenshot, y_pred_screenshot, average='macro', zero_division=0))

screenshot_report = classification_report(
    y_true_screenshot,
    y_pred_screenshot,
    labels=range(len(mlb_screenshot.classes_)),
    target_names=mlb_screenshot.classes_,
    output_dict=True,
    zero_division=0
)

# print("\nPer-label performance:\n", screenshot_report)

gold_ss_labels = set().union(*merged_df['screenshot_types_gold'])
pred_ss_labels = set().union(*merged_df['screenshot_types_pred'])
unexpected_predicted_ss_labels = pred_ss_labels - gold_ss_labels

if unexpected_predicted_ss_labels:
    print("⚠️ Predicted screenshot labels not found in gold standard:")
    print(unexpected_predicted_ss_labels)
else:
    print("✅ All predicted screenshot labels appear in gold standard.")

# Convert to DataFrame
screenshot_report_df = pd.DataFrame(screenshot_report).transpose()
# Save to CSV
screenshot_report_df.to_csv(f"screenshot_evaluation_report/{filename}_screenshotevaluation_report.csv", index=True)


# === Count False Positives for Logo Types ===
false_positive_logo_labels = []

for idx, row in merged_df.iterrows():
    gold = set(row['logo_types_gold'])
    pred = set(row['logo_types_pred'])
    false_positives = pred - gold
    for label in false_positives:
        false_positive_logo_labels.append(label)

fp_logo_counts = pd.Series(false_positive_logo_labels).value_counts()
print("\nFalse Positive Logo Labels (predicted but not in gold):")
print(fp_logo_counts)
# print(f"Total false positive logo labels: {len(false_positive_logo_labels)}")

# === Count False Positives for Screenshot Types ===
false_positive_ss_labels = []

for idx, row in merged_df.iterrows():
    gold = set(row['screenshot_types_gold'])
    pred = set(row['screenshot_types_pred'])
    false_positives = pred - gold
    for label in false_positives:
        false_positive_ss_labels.append(label)

fp_ss_counts = pd.Series(false_positive_ss_labels).value_counts()
print("\nFalse Positive Screenshot Labels (predicted but not in gold):")
print(fp_ss_counts)
# print(f"Total false positive screenshot labels: {len(false_positive_ss_labels)}")

# === Show False Positive Rows for Logo Types ===
fp_logo_rows = []

for idx, row in merged_df.iterrows():
    gold = set(row['logo_types_gold'])
    pred = set(row['logo_types_pred'])
    false_positives = pred - gold
    if false_positives:
        fp_logo_rows.append({
            "filename": row['filename'],
            "gold": gold,
            "predicted": pred,
            "false_positives": false_positives
        })

pd.set_option('display.max_colwidth', None)


fp_logo_df = pd.DataFrame(fp_logo_rows)
print("\n🔍 False Positive Rows: Logo Type Predictions")
print(fp_logo_df[['filename', 'gold', 'predicted', 'false_positives']])
fp_logo_df.to_csv(f"logo_evaluation_report/{filename}_false_positive_logo_rows.csv", index=False)

# === Count False Negatives for Logo Types ===
false_negative_logo_labels = []

for idx, row in merged_df.iterrows():
    gold = set(row['logo_types_gold'])
    pred = set(row['logo_types_pred'])
    false_negatives = gold - pred
    for label in false_negatives:
        false_negative_logo_labels.append(label)

fn_logo_counts = pd.Series(false_negative_logo_labels).value_counts()
print("\nFalse Negative Logo Labels (in gold but not predicted):")
print(fn_logo_counts)

# === Count False Negatives for Screenshot Types ===
false_negative_ss_labels = []

for idx, row in merged_df.iterrows():
    gold = set(row['screenshot_types_gold'])
    pred = set(row['screenshot_types_pred'])
    false_negatives = gold - pred
    for label in false_negatives:
        false_negative_ss_labels.append(label)

fn_ss_counts = pd.Series(false_negative_ss_labels).value_counts()
print("\nFalse Negative Screenshot Labels (in gold but not predicted):")
print(fn_ss_counts)

# === Show False Negative Rows for Logo Types ===
fn_logo_rows = []

for idx, row in merged_df.iterrows():
    gold = set(row['logo_types_gold'])
    pred = set(row['logo_types_pred'])
    false_negatives = gold - pred
    if false_negatives:
        fn_logo_rows.append({
            "filename": row['filename'],
            "gold": gold,
            "predicted": pred,
            "false_negatives": false_negatives
        })

fn_logo_df = pd.DataFrame(fn_logo_rows)
print("\n🔍 False Negative Rows: Logo Type Predictions")
print(fn_logo_df[['filename', 'gold', 'predicted', 'false_negatives']])
fn_logo_df.to_csv(f"logo_evaluation_report/{filename}_false_negative_logo_rows.csv", index=False)