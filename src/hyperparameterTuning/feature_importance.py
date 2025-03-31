import shap
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt

# Load the results
df = pd.read_csv("tuning_results.csv")

# Preparing the features and labels
X = df[["temperature", "top_p", "frequency_penalty", "presence_penalty"]]
y = df["success"]

# Simulating balance by adding fake 0s
if y.nunique() == 1:
    print("Warning: Only one class found in the target. Adding dummy failure examples for demo.")
    for _ in range(10):
        df = df._append({
            "temperature": 0.5,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "success": 0
        }, ignore_index=True)

    X = df[["temperature", "top_p", "frequency_penalty", "presence_penalty"]]
    y = df["success"]

# Training the XGBoost classifier
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
model.fit(X, y)

# Creating the SHAP explainer
explainer = shap.Explainer(model, X)
shap_values = explainer(X)

# Generating SHAP Summary Plot (Feature Importance)
plt.figure(figsize=(10, 10))
shap.summary_plot(shap_values, X, show=False)
plt.savefig("shap_summary_plot.png")
plt.show()