import json

def log_feedback(feedback_data):
    with open("feedback.json", "a") as f:
        json.dump(feedback_data, f)
        f.write("\n")
