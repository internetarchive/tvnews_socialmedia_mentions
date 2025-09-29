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

# ==========================
# Filenames / CSV paths
# ==========================
filename = "chatgpt40_CNN_cleaned_t5"

# chatgpt40_CNN_cleaned
# chatgpt40_FOXNEWS_cleaned
# chatgpt40_MSNBC_cleaned
# chatgpt40_CNN_cleaned_t5
# chatgpt40_MSNBC_cleaned_t5
# chatgpt40_FOXNEWS_cleaned_t5
# chatgpt40_CNN_t3_cleaned
# chatgpt40_CNN_t3_v2_cleaned
# chatgpt40_MSNBC_t3_v3_cleaned
# chatgpt40_FOXNEWS_t3_v3_cleaned
# chatgpt40_CNN_t3_v4_cleaned

gold_csv = "gold_standard/gold_standard_images_cnn_t5.csv"
pred_csv = f"cleaned/{filename}.csv"

# gold_standard_images_cnn
# gold_standard_images_cnn_adjusted
# gold_standard_images_foxnews
# gold_standard_images_foxnews_adjusted
# gold_standard_images_msnbc
# gold_standard_images_msnbc_adjusted
# gold_standard_images_cnn_t5
# gold_standard_images_msnbc_t5
# gold_standard_images_foxnews_t5
# gold_standard_images_cnn_t3
# gold_standard_images_cnn_t3_v2_
# gold_standard_images_msnbc_t3_v3_
# gold_standard_images_foxnews_t3_v3_
# gold_standard_images_cnn_t3_v4_.csv

# ==========================
# Load CSVs
# ==========================
gold_df = pd.read_csv(gold_csv)
chatgpt_df = pd.read_csv(pred_csv)

# ==========================
# Merge on filename
# ==========================
merged_df = pd.merge(
    chatgpt_df, gold_df, on="filename", how="left", suffixes=("_pred", "_gold")
)

# ==========================
# Helper Functions
# ==========================
def parse_labels(cell):
    """Convert comma-separated string to list of labels (lowercased)."""
    if isinstance(cell, str):
        return [label.strip().lower() for label in cell.split(',') if label.strip()]
    return []

def binary_detection_eval(prefix, y_true, y_pred):
    """Evaluate binary detection (yes/no) from boolean series."""
    cm = confusion_matrix(y_true.astype(int), y_pred.astype(int))
    tn, fp = cm[0,0], cm[0,1]
    fn, tp = cm[1,0], cm[1,1]

    print(f"\n=== {prefix.upper()} DETECTION (Binary yes/no) ===")
    print(f"                Predicted: Yes    Predicted: No")
    print(f"Actual: Yes        {tp:5}            {fn:5}")
    print(f"Actual: No         {fp:5}           {tn:5}")

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")

# ==========================
# Prepare type-level labels
# ==========================
# Logo
merged_df['logo_types_gold'] = merged_df['Social Media Logo Type_gold'].fillna("").apply(parse_labels)
merged_df['logo_types_pred'] = merged_df['Social Media Logo Type_pred'].fillna("").apply(parse_labels)

# Screenshot
merged_df['screenshot_types_gold'] = merged_df['Social Media Screenshot Type_gold'].fillna("").apply(parse_labels)
merged_df['screenshot_types_pred'] = merged_df['Social Media Screenshot Type_pred'].fillna("").apply(parse_labels)

# ==========================
# Binary detection derived from type-level labels
# ==========================
merged_df['binary_logo_gold'] = merged_df['logo_types_gold'].apply(lambda x: len(x) > 0)
merged_df['binary_logo_pred'] = merged_df['logo_types_pred'].apply(lambda x: len(x) > 0)

merged_df['binary_screenshot_gold'] = merged_df['screenshot_types_gold'].apply(lambda x: len(x) > 0)
merged_df['binary_screenshot_pred'] = merged_df['screenshot_types_pred'].apply(lambda x: len(x) > 0)

# ==========================
# Run Binary Evaluations
# ==========================
binary_detection_eval("logo", merged_df['binary_logo_gold'], merged_df['binary_logo_pred'])
binary_detection_eval("screenshot", merged_df['binary_screenshot_gold'], merged_df['binary_screenshot_pred'])

# ==========================
# Multi-label evaluation
# ==========================
def multilabel_eval(prefix, gold_list, pred_list, report_dir):
    all_labels = sorted(set().union(*gold_list) | set().union(*pred_list))
    all_labels = [label.lower() for label in all_labels]  # normalize

    mlb = MultiLabelBinarizer(classes=all_labels)
    mlb.fit([all_labels])  # ensure full label space
    y_true_type = mlb.transform(gold_list)
    y_pred_type = mlb.transform(pred_list)

    print(f"\n=== Evaluation: {prefix} Types (multi-label) ===")
    print("Labels:", mlb.classes_)

    report = classification_report(
        y_true_type,
        y_pred_type,
        target_names=mlb.classes_,
        labels=range(len(mlb.classes_)),
        output_dict=True,
        zero_division=0
    )

    # Warn on unexpected predicted-only labels
    gold_labels_set = set().union(*gold_list)
    pred_labels_set = set().union(*pred_list)
    unexpected_predicted_labels = pred_labels_set - gold_labels_set
    if unexpected_predicted_labels:
        print(f"⚠️ Predicted labels not found in gold standard ({prefix}):")
        print(unexpected_predicted_labels)
    else:
        print(f"✅ All predicted labels appear in gold standard ({prefix}).")

    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(f"{report_dir}/{filename}_{prefix}evaluation_report.csv", index=True)

    # False Positives
    fp_rows = []
    for idx, row in merged_df.iterrows():
        gold = set(row[gold_list.name])
        pred = set(row[pred_list.name])
        fp = pred - gold
        if fp:
            fp_rows.append({
                "filename": row['filename'],
                "gold": gold,
                "predicted": pred,
                "false_positives": fp
            })
    fp_df = pd.DataFrame(fp_rows)
    fp_df.to_csv(f"{report_dir}/{filename}_false_positive_{prefix}_rows.csv", index=False)

    # False Negatives
    fn_rows = []
    for idx, row in merged_df.iterrows():
        gold = set(row[gold_list.name])
        pred = set(row[pred_list.name])
        fn = gold - pred
        if fn:
            fn_rows.append({
                "filename": row['filename'],
                "gold": gold,
                "predicted": pred,
                "false_negatives": fn
            })
    fn_df = pd.DataFrame(fn_rows)
    fn_df.to_csv(f"{report_dir}/{filename}_false_negative_{prefix}_rows.csv", index=False)

    return report_df, fp_df, fn_df

# ==========================
# Logo Evaluation
# ==========================
logo_report_df, logo_fp_df, logo_fn_df = multilabel_eval(
    "logo",
    merged_df['logo_types_gold'],
    merged_df['logo_types_pred'],
    report_dir="logo_evaluation_report"
)

# ==========================
# Screenshot Evaluation
# ==========================
screenshot_report_df, screenshot_fp_df, screenshot_fn_df = multilabel_eval(
    "screenshot",
    merged_df['screenshot_types_gold'],
    merged_df['screenshot_types_pred'],
    report_dir="screenshot_evaluation_report"
)

print("\n✅ Evaluation Complete")
