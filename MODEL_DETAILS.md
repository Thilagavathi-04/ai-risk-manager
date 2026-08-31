# AI Risk Manager — Machine Learning Model Documentation

This document provides a detailed technical overview of the machine learning models, preprocessing pipelines, hyperparameters, evaluation metrics, and operational decision policies implemented in the **AI Risk Manager** system.

---

## 1. Overview of Models

The system implements a comparative ML architecture featuring an active production classifier and a baseline benchmark model.

### 🌲 Active Model: Histogram-Based Gradient Boosted Trees
* **Algorithm**: `sklearn.ensemble.HistGradientBoostingClassifier`
* **Implementation Location**: [`ml_pipeline/train.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/train.py#L60-L65)
* **Serialized Artifact**: `artifacts/risk_model.joblib`
* **MLflow Model Name**: `model` (under experiment `ai-risk-manager-paysim1`)
* **Role**: Primary real-time risk scoring engine for payment transactions.

#### Hyperparameters
| Parameter | Value | Description |
| :--- | :--- | :--- |
| `max_depth` | `6` | Limits maximum depth of individual decision trees to prevent overfitting |
| `learning_rate` | `0.08` | Shrinkage factor applied to update steps during gradient boosting |
| `max_iter` | `150` | Maximum number of boosting iterations (trees) |

---

### 📊 Baseline Model: Logistic Regression
* **Algorithm**: `sklearn.linear_model.LogisticRegression`
* **Implementation Location**: [`ml_pipeline/train.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/train.py#L53-L58)
* **Serialized Artifact**: `artifacts/baseline_model.joblib`
* **Role**: Benchmark model used on the Evaluation dashboard to quantify the performance lift of the tree model.

#### Hyperparameters
| Parameter | Value | Description |
| :--- | :--- | :--- |
| `max_iter` | `1000` | Convergence iteration limit |
| `class_weight` | `"balanced"` | Adjusts weights inversely proportional to class frequencies to handle imbalanced data |

---

## 2. Feature Engineering & Preprocessing Pipeline

The model pipeline relies on scikit-learn `Pipeline` and `ColumnTransformer` ([`ml_pipeline/preprocessing.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/preprocessing.py#L9-L30)):

```
Raw Transaction Input 
     │
     ├── Numeric Features (amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, step)
     │     └── SimpleImputer(median) ──► StandardScaler()
     │
     └── Categorical Features (type: PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT)
           └── SimpleImputer(most_frequent) ──► OneHotEncoder(handle_unknown="ignore", sparse_output=False)
```

---

## 3. Decision Policy & Threshold Calibration

* **Decision Threshold**: `0.72` ([`ml_pipeline/threshold.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/threshold.py))
* **Risk Categorization Rules** ([`ml_pipeline/predict.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/predict.py#L23-L32)):
  * **Risk Score $\ge$ 0.72**: Risk Level **HIGH** $\rightarrow$ Action **Manual Review**
  * **0.36 $\le$ Risk Score < 0.72**: Risk Level **MEDIUM** $\rightarrow$ Action **Verification**
  * **Risk Score < 0.36**: Risk Level **LOW** $\rightarrow$ Action **Approve**

---

## 4. Performance Metrics & Comparative Analysis

The model evaluation was conducted on a 15% temporal held-out test split (~954,393 test rows from the 6,362,620 row PaySim dataset):

| Metric | Active Model (**Boosted Tree**) | Notes |
| :--- | :---: | :--- |
| **Precision** | **99.41%** | Minimal false positive rate; ensures legitimate customer transactions are rarely blocked |
| **Recall** | **71.48%** | Direct fraud detection rate captured prior to threshold tuning |
| **F1 Score** | **83.16%** | Harmonic mean of precision and recall |
| **PR-AUC** | **86.07%** | Area under Precision-Recall curve |
| **ROC-AUC** | **96.78%** | Overall model discrimination power |

---

## 5. Cost Model Assumptions

To evaluate real-world trade-offs between false positives (analyst workload) and false negatives (fraud loss):
* **False Positive Cost ($C_{FP}$)**: ₹20 (cost of manual analyst verification time)
* **False Negative Cost ($C_{FN}$)**: ₹500 (average direct fraud loss)
* **Manual Review Unit Cost ($C_{REV}$)**: ₹10

---

## 6. Real-Time Inference & Explainability

* **Scoring Endpoint**: `POST /api/v1/predict` ([`routes/v1/api.py`](file:///Thilaga/Projects/ai-risk-manager/routes/v1/api.py#L33-L52))
* **Reason Signal Extraction**: [`ml_pipeline/predict.py`](file:///Thilaga/Projects/ai-risk-manager/ml_pipeline/predict.py#L35-L44) surfaces human-interpretable risk drivers such as balance drop triggers and high transfer amount anomalies.
