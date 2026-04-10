"""
Project: AI Lead Classification Tool
Description: Classifies leads into priority categories using AI
"""

from transformers import pipeline
import pandas as pd

# ==============================
# 1. Load AI Model
# ==============================
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ==============================
# 2. Sample Lead Data
# ==============================
data = {
    "Lead_Name": ["John Corp", "Sarah Smith", "Tech Hub UI", "Mike Ross"],
    "Description": [
        "Interested in buying 50 units of luxury furniture.",
        "Wants to buy a single chair.",
        "Looking for a full office redesign and premium desks.",
        "Just browsing for prices."
    ]
}

df = pd.DataFrame(data)

# ==============================
# 3. Labels
# ==============================
labels = ["High Priority Business", "Low Priority Individual"]

# ==============================
# 4. Classification Function
# ==============================
def classify_lead(text):
    result = classifier(text, labels)
    return result["labels"][0], result["scores"][0]

# ==============================
# 5. Apply Classification
# ==============================
lead_types = []
confidences = []

for text in df["Description"]:
    lead_type, confidence = classify_lead(text)
    lead_types.append(lead_type)
    confidences.append(round(confidence, 2))

df["Lead_Type"] = lead_types
df["Confidence"] = confidences

# ==============================
# 6. Save Output
# ==============================
df.to_csv("classified_leads.csv", index=False)

print("\n✅ Classification Complete:\n")
print(df)
