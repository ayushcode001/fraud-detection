import streamlit as st
import pandas as pd
import joblib

# Load the model with Streamlit's caching mechanism
@st.cache_resource
def load_model():
    return joblib.load('fraud_detection_pipeline.pkl')

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")

# Page config configuration (native)
st.set_page_config(
    page_title="Fraud Detection Predictor",
    page_icon="🛡️",
    layout="centered"
)

# Helper function to apply presets to session state
def apply_preset(tx_type, amt, old_org, new_org, old_dest, new_dest):
    st.session_state.transaction_type = tx_type
    st.session_state.amount = amt
    st.session_state.oldbalanceOrg = old_org
    st.session_state.newbalanceOrig = new_org
    st.session_state.oldbalanceDest = old_dest
    st.session_state.newbalanceDest = new_dest

# Initialize session state variables if not already defined
if 'transaction_type' not in st.session_state:
    st.session_state.transaction_type = 'PAYMENT'
if 'amount' not in st.session_state:
    st.session_state.amount = 1000.0
if 'oldbalanceOrg' not in st.session_state:
    st.session_state.oldbalanceOrg = 10000.0
if 'newbalanceOrig' not in st.session_state:
    st.session_state.newbalanceOrig = 9000.0
if 'oldbalanceDest' not in st.session_state:
    st.session_state.oldbalanceDest = 10000.0
if 'newbalanceDest' not in st.session_state:
    st.session_state.newbalanceDest = 10000.0

# Sidebar configuration (native elements only)
st.sidebar.title("Scenario Presets")
st.sidebar.write("Load predefined test values:")

if st.sidebar.button("Standard Legitimate Payment"):
    apply_preset('PAYMENT', 1500.0, 5000.0, 3500.0, 10000.0, 11500.0)
    
if st.sidebar.button("High-Value Transfer (Suspicious)"):
    apply_preset('TRANSFER', 85000.0, 120000.0, 35000.0, 0.0, 85000.0)

if st.sidebar.button("Balance Exhaustion (Fraud Pattern)"):
    apply_preset('TRANSFER', 250000.0, 250000.0, 0.0, 0.0, 0.0)

if st.sidebar.button("Standard Cash Out"):
    apply_preset('CASH_OUT', 45000.0, 60000.0, 15000.0, 45000.0, 90000.0)

st.sidebar.divider()

st.sidebar.subheader("Engine Diagnostics")
st.sidebar.text(
    "Model Pipeline: XGBoost\n"
    "Train Size: 6.36 Million\n"
    "Model Version: v1.1.0-prod\n"
    "Precision: 81.0%\n"
    "Recall: 76.5%\n"
    "ROC-AUC Score: 99.8%"
)

# Main page header
st.title("Fraud Detection Predictor")
st.write("Enter the transaction details to evaluate risk assessment indicators.")
st.divider()

# Input layout using native columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Transaction settings")
    transaction_type = st.selectbox(
        "Transaction Type", 
        ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEPOSIT'], 
        key='transaction_type'
    )
    amount = st.number_input(
        "Amount ($)", 
        min_value=0.0, 
        key='amount'
    )
    
    st.subheader("Origin Account Status")
    oldbalanceOrg = st.number_input(
        'Old Balance (Sender) ($)', 
        min_value=0.0, 
        key='oldbalanceOrg'
    )
    newbalanceOrig = st.number_input(
        'New Balance (Sender) ($)', 
        min_value=0.0, 
        key='newbalanceOrig'
    )
    
with col2:
    st.subheader("Destination Account Status")
    oldbalanceDest = st.number_input(
        'Old Balance (Receiver) ($)', 
        min_value=0.0, 
        key='oldbalanceDest'
    )
    newbalanceDest = st.number_input(
        'New Balance (Receiver) ($)', 
        min_value=0.0, 
        key='newbalanceDest'
    )
    
    st.subheader("Rule-based Checks")
    # Real-time warnings
    rule_alerts = []
    if amount > oldbalanceOrg:
        rule_alerts.append("Overdraft: Transaction value exceeds the origin account's balance.")
        
    expected_new_org = oldbalanceOrg - amount
    if transaction_type in ['TRANSFER', 'CASH_OUT'] and abs(newbalanceOrig - expected_new_org) > 0.01:
        rule_alerts.append(f"Inconsistency: Expected Sender balance is ${expected_new_org:,.2f}.")
        
    expected_new_dest = oldbalanceDest + amount
    if transaction_type in ['TRANSFER', 'DEPOSIT'] and abs(newbalanceDest - expected_new_dest) > 0.01:
        rule_alerts.append(f"Inconsistency: Expected Receiver balance is ${expected_new_dest:,.2f}.")
        
    if not rule_alerts:
        st.success("Cash flow metrics are consistent.")
    else:
        for alert in rule_alerts:
            st.warning(alert)

# Action button
st.divider()
predict_btn = st.button("Run Risk Assessment Engine", use_container_width=True)

if predict_btn:
    # Build payload DataFrame
    input_data = pd.DataFrame([{
        'type' : transaction_type,
        "amount" : amount,
        "oldbalanceOrg" : oldbalanceOrg,
        "newbalanceOrig" : newbalanceOrig,
        'oldbalanceDest' : oldbalanceDest,
        "newbalanceDest" : newbalanceDest
    }])
    
    try:
        # Run prediction
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
        fraud_prob = probabilities[1]
        
        st.subheader("Engine Prediction Report")
        
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            st.write(f"**Calculated Fraud Probability:** {fraud_prob * 100:.2f}%")
            st.progress(float(fraud_prob))
            
            if prediction == 1:
                st.error("This transaction can be fraud")
            else:
                st.success("This transaction looks like it is not a fraud")
                
        with col_r2:
            st.write("**Balance Shift Visualization:**")
            plot_df = pd.DataFrame({
                'Before': [oldbalanceOrg, oldbalanceDest],
                'After': [newbalanceOrig, newbalanceDest]
            }, index=['Sender', 'Receiver'])
            st.bar_chart(plot_df)
            
    except Exception as prediction_error:
        st.error(f"Prediction logic error: {prediction_error}")
