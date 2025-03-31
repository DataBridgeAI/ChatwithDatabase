import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.ensemble import RandomForestClassifier

# Load the results csv file
df = pd.read_csv("tuning_results.csv")

output_dir = "."
os.makedirs(output_dir, exist_ok=True)

print("\n=== Summary of Hyperparameter Tuning ===\n")
print(df.describe(include='all'))

# Filter successful runs
success_df = df[df['success'] == 1]

# Execution Time vs Temperature (successful runs)
if not success_df.empty:
    plt.figure(figsize=(10, 6))
    plt.scatter(
        success_df["temperature"],
        success_df["execution_time"],
        c="blue",
        alpha=0.6
    )
    for i, row in success_df.iterrows():
        plt.text(row["temperature"], row["execution_time"], f"{row['top_p']},{row['frequency_penalty']},{row['presence_penalty']}", fontsize=8)
    plt.title("Execution Time vs Temperature (Successful Runs)")
    plt.xlabel("Temperature")
    plt.ylabel("Execution Time (s)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "execution_time_vs_temperature.png"))
    plt.show()
else:
    print("No successful runs to visualize.")

# Convert success to categorical
df['success_label'] = df['success'].map({1: 'Success', 0: 'Failure'})

# Success vs Failure Counts
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='success_label', palette='Set2')
plt.title("Success vs Failure Counts")
plt.xlabel("Outcome")
plt.ylabel("Count")
plt.savefig(os.path.join(output_dir, "success_vs_failure.png"))
plt.show()

# Execution Time Distribution (Successes Only)
plt.figure(figsize=(8, 5))
sns.histplot(data=success_df, x='execution_time', bins=10, kde=True)
plt.title("Execution Time Distribution (Successful Runs)")
plt.xlabel("Execution Time (s)")
plt.ylabel("Frequency")
plt.savefig(os.path.join(output_dir, "execution_time_distribution_success.png"))
plt.show()

# Bar Plot: Success/Failure by Temperature
temp_success = pd.crosstab(df["temperature"], df["success_label"])
temp_success.plot(kind="bar", stacked=True, colormap="Set3", figsize=(8, 5))
plt.title("Success/Failure by Temperature")
plt.xlabel("Temperature")
plt.ylabel("Count")
plt.savefig(os.path.join(output_dir, "success_by_temperature.png"))
plt.show()

# Top Performing Configurations by Execution Time
top_configs = success_df.sort_values(by='execution_time').head(10)
print("\n Top 10 Fastest Successful Configurations \n")
print(top_configs[["temperature", "top_p", "frequency_penalty", "presence_penalty", "execution_time"]])

# Hyperparameter Sensitivity Analysis
features = df[["temperature", "top_p", "frequency_penalty", "presence_penalty"]]
labels = df["success"]

model = RandomForestClassifier(random_state=42)
model.fit(features, labels)

importances = model.feature_importances_
importance_df = pd.DataFrame({
    "Hyperparameter": features.columns,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\n Hyperparameter Sensitivity - Feature Importance Analysis\n")
print(importance_df)

# Plot feature importances
plt.figure(figsize=(6, 4))
sns.barplot(x="Importance", y="Hyperparameter", data=importance_df, palette="viridis")
plt.title("Hyperparameter Sensitivity")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "hyperparameter_sensitivity.png"))
plt.show()