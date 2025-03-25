# src/hyperparameterTuning/tuning_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from src.monitoring.mlflow_config import QueryTracker  # Corrected import

# Initialize QueryTracker
tracker = QueryTracker()

# Load the results
df = pd.read_csv("tuning_results.csv")

print("\n=== Summary of Hyperparameter Tuning ===\n")
print(df.describe(include='all'))

# Filter successful runs
success_df = df[df['success'] == 1]

# 1. Plot: Execution Time vs Temperature (successful runs)
if not success_df.empty:
    plt.figure(figsize=(10, 6))
    plt.scatter(
        success_df["temperature"],
        success_df["execution_time"],
        c="blue",
        alpha=0.6
    )
    for i, row in success_df.iterrows():
        plt.text(row["temperature"], row["execution_time"], 
                 f"{row['top_p']},{row['frequency_penalty']},{row['presence_penalty']}", fontsize=8)
    plt.title("Execution Time vs Temperature (Successful Runs)")
    plt.xlabel("Temperature")
    plt.ylabel("Execution Time (s)")
    plt.grid(True)
    plt.tight_layout()
    tracker.log_visualization("execution_time_vs_temperature")
    plt.show()
else:
    print("No successful runs to visualize.")

# Convert success to categorical
df['success_label'] = df['success'].map({1: 'Success', 0: 'Failure'})

# 2. Plot: Success vs Failure Counts
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='success_label', palette='Set2')
plt.title("Success vs Failure Counts")
plt.xlabel("Outcome")
plt.ylabel("Count")
tracker.log_visualization("success_vs_failure")
plt.show()

# 3. Plot: Execution Time Distribution (Successes Only)
plt.figure(figsize=(8, 5))
sns.histplot(data=success_df, x='execution_time', bins=10, kde=True)
plt.title("Execution Time Distribution (Successful Runs)")
plt.xlabel("Execution Time (s)")
plt.ylabel("Frequency")
tracker.log_visualization("execution_time_distribution_success")
plt.show()

# 4. Pairplot for Hyperparameters colored by Success
sns.pairplot(df, vars=["temperature", "top_p", "frequency_penalty", "presence_penalty"], 
             hue="success_label", palette="husl")
tracker.log_visualization("hyperparameter_pairplot")
plt.show()

# 5. Heatmap of Parameter Correlations
correlation_data = df[["temperature", "top_p", "frequency_penalty", "presence_penalty", "success"]]
correlation_matrix = correlation_data.corr()
plt.figure(figsize=(8, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
tracker.log_visualization("correlation_matrix")
plt.show()

# 6. Bar Plot: Successasc
temp_success = pd.crosstab(df["temperature"], df["success_label"])
temp_success.plot(kind="bar", stacked=True, colormap="Set3", figsize=(8, 5))
plt.title("Success/Failure by Temperature")
plt.xlabel("Temperature")
plt.ylabel("Count")
tracker.log_visualization("success_by_temperature")
plt.show()

# 7. Top Performing Configurations by Execution Time
top_configs = success_df.sort_values(by='execution_time').head(10)
print("\n=== Top 10 Fastest Successful Configurations ===\n")
print(top_configs[["temperature", "top_p", "frequency_penalty", "presence_penalty", "execution_time"]])