"""
Evaluate against manual labels on images 
This is more direct than evaluate.py but the draw back is we need manual labels for each image (not clip URLs)
"""
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

# Load data
gold_df = pd.read_csv('gold_standard_images.csv')
pred_df = pd.read_csv('gemini2flashexp_results.csv')

# Merge on filename
merged_df = pd.merge(gold_df, pred_df, on='filename', suffixes=('_gold', '_pred'))

# Normalize Yes/No detection labels to lowercase and strip whitespace
y_true_logo = merged_df['Social Media Logo_gold'].str.strip().str.lower()
y_pred_logo = merged_df['Social Media Logo_pred'].str.strip().str.lower()

print("=== Evaluation: Social Media Logo Presence (yes/no) ===")
print(confusion_matrix(y_true_logo, y_pred_logo))
print(classification_report(y_true_logo, y_pred_logo, zero_division=0))


# Helper to parse and lowercase multi-label strings into sets
def parse_types(value):
    if pd.isna(value) or value.strip().lower() == 'no' or value.strip() == '':
        return set()
    return set(map(lambda x: x.strip().lower(), value.split(',')))


# Normalize predicted label sets with your custom logic
def normalize_predicted_labels(label_set):
    cleaned = set()

    # Clean raw labels: lowercase + remove 'logo'
    stripped = {label.lower().replace('logo', '').strip() for label in label_set}

    has_twitter = any(label == "twitter" for label in stripped)
    has_x_variant = any(label in {"x", "x (formerly twitter)", "x (twitter)"} for label in stripped)

    # Apply your Twitter/X logic
    if has_twitter and has_x_variant:
        cleaned.add("twitter (x)")
    elif has_x_variant:
        cleaned.add("twitter (x)")
    elif has_twitter:
        cleaned.add("twitter")

    # Handle Parler and other labels
    for label in stripped:
        if label == "twitter" or label in {"x", "x (formerly twitter)", "x (twitter)"}:
            continue  # already handled above
        elif "parler" in label:
            cleaned.add("parler")
        else:
            cleaned.add(label)

    return cleaned


# Apply parsing to both gold and predicted columns
merged_df['logo_types_gold'] = merged_df['Social Media Logo Type_gold'].apply(parse_types)
merged_df['logo_types_pred'] = merged_df['Social Media Logo Type_pred'].apply(parse_types).apply(normalize_predicted_labels)

# Use MultiLabelBinarizer to encode multi-label sets as binary indicator vectors
mlb = MultiLabelBinarizer()
y_true_type = mlb.fit_transform(merged_df['logo_types_gold'])
y_pred_type = mlb.transform(merged_df['logo_types_pred'])

print("\n=== Evaluation: Social Media Logo Types (multi-label classification) ===")
print("Labels:", mlb.classes_)
print("Precision (macro):", precision_score(y_true_type, y_pred_type, average='macro', zero_division=0))
print("Recall (macro):", recall_score(y_true_type, y_pred_type, average='macro', zero_division=0))
print("F1-score (macro):", f1_score(y_true_type, y_pred_type, average='macro', zero_division=0))

# Detailed per-label report
report = classification_report(y_true_type, y_pred_type, target_names=mlb.classes_, zero_division=0)
print("\nPer-label performance:\n", report)


# Optional: Print predicted labels not in gold (for debugging)
gold_labels = set().union(*merged_df['logo_types_gold'])
pred_labels = set().union(*merged_df['logo_types_pred'])
unexpected_predicted_labels = pred_labels - gold_labels
if unexpected_predicted_labels:
    print("⚠️ Predicted labels not found in gold standard:")
    print(unexpected_predicted_labels)
else:
    print("✅ All predicted labels appear in gold standard.")

