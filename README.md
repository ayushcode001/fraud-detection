# Fraud Detection Predictor 🛡️

A real-time financial transaction risk diagnostics dashboard powered by **XGBoost** and **Streamlit**. The system assesses transactions for potential fraud patterns (such as cash-out theft or account balance depletion) using machine learning.

---

## 📊 Model Performance

The predictive model is trained on a synthetic dataset of **6.36 million financial transactions** and evaluated using key classification metrics:

* **Precision (Fraud Class)**: `81.0%`
* **Recall (Fraud Class)**: `76.5%`
* **ROC-AUC Score**: `99.8%`
* **Core Classifier**: XGBoost Classifier (inside an Scikit-learn Pipeline with Standard Scaler and One-Hot Encoding).

---

## 🚀 Key Features

* **Performance Caching**: Employs Streamlit `@st.cache_resource` memory loading to avoid disk IO bottlenecks and reload the model only once.
* **Interactive Scenario Presets**: One-click buttons in the sidebar to load specific transactional testcases dynamically:
  * 🟢 Legitimate Payment
  * 🟡 High-Value Transfer (Suspicious)
  * 🔴 Balance Exhaustion (Fraud Pattern)
  * 🔵 Standard Cash Out
* **Cash Flow Diagnostic Rules**: Real-time evaluation of inputs to alert users of overdrafts or balance inconsistencies (e.g. sender/receiver balances not matching the transaction amount).
* **Risk Profiling & Probability**: Calculates the exact probability percentage of fraud risk and marks the transaction under clear Risk Levels (Low, Medium, or High Risk).
* **Visual Balance Shift Charts**: Compares the Origin and Destination account balances before and after the transaction side-by-side using interactive bar charts.

---

## 💻 Local Installation and Setup

### Prerequisites
Make sure you have Python 3.9+ installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/ayushcode001/fraud-detection.git
cd fraud-detection
```

### 2. Configure Virtual Environment
Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright browser binary (For keep-awake checks)
```bash
playwright install chromium
```

### 5. Run the Streamlit Application
```bash
streamlit run fraud_detection.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## ⚙️ Uptime Maintenance with `keep_alive.py`

Streamlit Community Cloud hibernates free apps after a period of inactivity (typically 12 hours) and displays a "Yes, get this app back up!" prompt. 

To keep the application awake, the [keep_alive.py](keep_alive.py) script can be run periodically as a cron job or scheduled task. It navigates to the app URL headlessly and clicks the wake-up button if sleep mode is detected.

### Windows (Task Scheduler)
1. Open **Task Scheduler** and click **Create Basic Task**.
2. Set Trigger to repeat every **30 minutes**.
3. Under Action, choose **Start a Program**:
   * Program/Script: `C:\path\to\your\fraud-detection\.venv\Scripts\python.exe`
   * Arguments: `keep_alive.py <YOUR_DEPLOYED_APP_URL>`
   * Start in: `C:\path\to\your\fraud-detection`

### Linux / Mac (crontab)
To query the app every 30 minutes, add this line to your crontab:
```bash
*/30 * * * * /path/to/your/fraud-detection/.venv/bin/python /path/to/your/fraud-detection/keep_alive.py <YOUR_DEPLOYED_APP_URL> >> /path/to/your/keep_alive.log 2>&1
```