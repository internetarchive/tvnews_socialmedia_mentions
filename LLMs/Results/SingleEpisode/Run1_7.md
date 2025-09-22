# Evaluation – Social Media Logo & Screenshot Detection

## Summary

### Logo Detection (Runs 1–7)

| Run | Predicted: Yes (Actual: Yes / No) | Predicted: No (Actual: Yes / No) | Accuracy | Precision | Recall | F1 |
|-----|-----------------------------------|---------------------------------|----------|-----------|--------|----|
| 1   | 64 / 399                          | 7 / 3191                        | 0.8891   | 0.1382    | 0.9014 | 0.2397 |
| 2   | 67 / 388                          | 4 / 3202                        | 0.8929   | 0.1473    | 0.9437 | 0.2548 |
| 3   | 66 / 505                          | 5 / 3085                        | 0.8607   | 0.1156    | 0.9296 | 0.2056 |
| 4   | 65 / 492                          | 6 / 3098                        | 0.8640   | 0.1167    | 0.9155 | 0.2070 |
| 5   | 67 / 472                          | 4 / 3118                        | 0.8700   | 0.1243    | 0.9437 | 0.2197 |
| 6   | 67 / 452                          | 4 / 3138                        | 0.8754   | 0.1291    | 0.9437 | 0.2271 |
| 7   | 66 / 479                          | 5 / 3111                        | 0.8678   | 0.1211    | 0.9296 | 0.2143 |

---

### Screenshot Detection (Runs 1–7)

| Run | Predicted: Yes (Actual: Yes / No) | Predicted: No (Actual: Yes / No) | Accuracy | Precision | Recall | F1 |
|-----|-----------------------------------|---------------------------------|----------|-----------|--------|----|
| 1   | 55 / 3                             | 0 / 3603                        | 0.9992   | 0.9483    | 1.0000 | 0.9735 |
| 2   | 55 / 2                             | 0 / 3604                        | 0.9995   | 0.9649    | 1.0000 | 0.9821 |
| 3   | 55 / 0                             | 0 / 3606                        | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 4   | 55 / 0                             | 0 / 3606                        | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 5   | 55 / 0                             | 0 / 3606                        | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 6   | 55 / 0                             | 0 / 3606                        | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 7   | 55 / 1                             | 0 / 3605                        | 0.9997   | 0.9821    | 1.0000 | 0.9910 |

## Performance Metrics


| Run | Prompt | Temp | Task       | Accuracy | Precision | Recall | F1    |
|-----|--------|------|------------|----------|-----------|--------|-------|
| 1   | v2     | —    | Logo       | 0.8891   | 0.1382    | 0.9014 | 0.2397 |
|     |        |      | Screenshot | 0.9992   | 0.9483    | 1.0000 | 0.9735 |
| 2   | v2     | —    | Logo       | 0.8929   | 0.1473    | 0.9437 | 0.2548 |
|     |        |      | Screenshot | 0.9995   | 0.9649    | 1.0000 | 0.9821 |
| 3   | v2     | 0.2  | Logo       | 0.8607   | 0.1156    | 0.9296 | 0.2056 |
|     |        |      | Screenshot | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 4   | v2     | 0.2  | Logo       | 0.8640   | 0.1167    | 0.9155 | 0.2070 |
|     |        |      | Screenshot | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 5   | v2     | 0.0  | Logo       | 0.8700   | 0.1243    | 0.9437 | 0.2197 |
|     |        |      | Screenshot | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 6   | v2     | 0.0  | Logo       | 0.8754   | 0.1291    | 0.9437 | 0.2271 |
|     |        |      | Screenshot | 1.0000   | 1.0000    | 1.0000 | 1.0000 |
| 7   | v2     | 0.0  | Logo       | 0.8678   | 0.1211    | 0.9296 | 0.2143 |
|     |        |      | Screenshot | 0.9997   | 0.9821    | 1.0000 | 0.9910 |


## Confusion Matrix

### Run 1 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 64             | 7             |
| **Actual: No**  | 399            | 3191          |

### Run 1 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 3              | 3603          |

### Run 2 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 67             | 4             |
| **Actual: No**  | 388            | 3202          |

### Run 2 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 2              | 3604          |

### Run 3 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 66             | 5             |
| **Actual: No**  | 505            | 3085          |

### Run 3 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 0              | 3606          |

### Run 4 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 65             | 6             |
| **Actual: No**  | 492            | 3098          |

### Run 4 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 0              | 3606          |

### Run 5 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 67             | 4             |
| **Actual: No**  | 472            | 3118          |

### Run 5 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 0              | 3606          |

### Run 6 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 67             | 4             |
| **Actual: No**  | 452            | 3138          |

### Run 6 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 0              | 3606          |

### Run 7 – Logo Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 66             | 5             |
| **Actual: No**  | 479            | 3111          |

### Run 7 – Screenshot Detection

|                | Predicted: Yes | Predicted: No |
|----------------|----------------|---------------|
| **Actual: Yes** | 55             | 0             |
| **Actual: No**  | 1              | 3605          |
