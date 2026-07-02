# Financial Transaction Fraud Detection — End-to-End ML Pipeline
Turn 6.36M raw transaction logs into real-time fraud prevention alerts — from data ingestion to a live, interactive dashboard.

Live Demo → [Fraud Detection](https://fraud-detection-weba.streamlit.app/)

## Problem Statement
A global financial payment company processes **6.36 million transactions** generated over a simulated time window. The risk assessment team has no systematic way to:

* Identify and block fraudulent transfers before funds are permanently drawn.
* Distinguish normal high-value cash-outs from structural theft patterns.
* Minimize false positives to avoid blocking legitimate user accounts.
* Handle highly imbalanced transaction profiles (only 8,213 fraud cases out of 6.36M transactions, ~0.13%).

**Goal**: Build an XGBoost-based classification pipeline that automatically detects fraud patterns in real-time and serves them through a high-performance Streamlit dashboard.

---

## Approach & Methodology

### Data Engineering & Cleaning
* Normalized features including transaction type, sender balances, and receiver balances.
* Checked for zero/negative values in monetary transaction entries.
* Filtered transaction types to isolate high-risk actions (`TRANSFER` and `CASH_OUT`).

### Feature Engineering — Financial Indicators
* **Recency / Step**: Transaction timestamp represented as steps.
* **Monetary Value**: Actual transaction amount in BRL/USD.
* **Origin Balance Difference**: Discrepancy check between expected new balance (`oldbalanceOrg - amount`) and actual balance.
* **Destination Balance Difference**: Discrepancy check between expected new balance (`oldbalanceDest + amount`) and actual balance.

| Feature | Description | Business Signal |
| :--- | :--- | :--- |
| **type** | Categorical transaction profile (One-Hot Encoded) | Basic transaction intent |
| **amount** | Transaction value | Financial weight of transaction |
| **oldbalanceOrg / newbalanceOrig** | Origin sender account state | Origin account depletion rate |
| **oldbalanceDest / newbalanceDest** | Destination receiver account state | Target account growth pattern |

### Modeling — XGBoost Classification
* `StandardScaler` normalization applied to all numerical columns (`amount`, sender/receiver balances).
* `OneHotEncoder(drop='first')` applied to the categorical column `type`.
* Model: `XGBClassifier` with `learning_rate=0.1` and `max_depth=4` optimized for extreme class imbalance using PR (Precision-Recall) evaluation metrics.
* Serialization: Entire scaling and prediction pipeline exported using `joblib`.

### Deployment — Streamlit Cloud + Playwright Uptime
* Dashboard handles input updates via standard Streamlit widgets.
* Integrated [keep_alive.py](keep_alive.py) checks utilizing Chromium via Playwright to simulate browser traffic and click wake-up buttons if sleep mode occurs.

---

## 🎯 Fraud Risk Classifications

| Risk Level | Profile | Recommended Action |
| :--- | :--- | :--- |
| **High Risk (> 50%)** | Matches clear cash theft and balance exhaustion patterns. | Block transaction immediately, flag account. |
| **Medium Risk (15% - 50%)** | Structural anomalies present. | Trigger two-factor authentication or manual review. |
| **Low Risk (< 15%)** | Safe transaction. | Allow transaction to clear immediately. |

---

## Project Architecture

```
fraud-detection/
├── analysis_model.ipynb        # Jupyter notebook detailing data analysis & training
├── fraud_detection.py          # Native Streamlit dashboard application
├── keep_alive.py               # Playwright browser keep-awake monitor script
├── fraud_detection_pipeline.pkl # Pickled machine learning model pipeline
├── requirements.txt            # Pinned dependencies
└── .gitignore                  # Git exclusions for .venv & cache directories
```

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Data Processing** | Pandas, NumPy, Scikit-Learn | ETL, scale transformers, one-hot encoding |
| **Visualization** | Streamlit Native Charts | Dynamic balance shift tracking |
| **Machine Learning** | XGBoost (XGBClassifier) | Classification modeling |
| **Model Serving** | Joblib | Model pipeline serialization |
| **Frontend** | Streamlit | Input panels and risk reporting |
| **Automation** | Playwright (Python) | Headless browser uptime monitor |

---

## Quick Start

### Prerequisites
* Python 3.11+
* Git

### Installation
```bash
git clone https://github.com/ayushcode001/fraud-detection.git
cd fraud-detection
pip install -r requirements.txt
playwright install chromium
```

### Launch Dashboard
```bash
streamlit run fraud_detection.py
```

### Launch Uptime check
```bash
python keep_alive.py http://localhost:8501
```

---

## Key Results

| Metric | Value |
| :--- | :--- |
| **Total transactions processed** | 6,362,620 |
| **Fraudulent events captured** | 8,213 |
| **Classifier model** | XGBoost Classifier |
| **Precision** | `81.0%` |
| **Recall** | `76.5%` |
| **ROC-AUC** | `99.8%` |

---

## Model Pipeline Reference

```python
import joblib
import pandas as pd

# Load the trained model pipeline
model = joblib.load('fraud_detection_pipeline.pkl')

# Construct transaction payload
input_data = pd.DataFrame([{
    'type': 'TRANSFER',
    'amount': 250000.0,
    'oldbalanceOrg': 250000.0,
    'newbalanceOrig': 0.0,
    'oldbalanceDest': 0.0,
    'newbalanceDest': 0.0
}])

# Predict risk probabilities
probabilities = model.predict_proba(input_data)[0]
print(f"Calculated Fraud Probability: {probabilities[1] * 100:.2f}%")
```
