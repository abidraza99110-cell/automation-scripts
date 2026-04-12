"""
Project: AI Lead Bulk Processor

Description:
Processes large lead datasets and classifies them into decision-makers
and contributors using AI, with confidence scoring and review flags.
"""
import pandas as pd
from transformers import pipeline

print("please upload your csv file")
file_name=input("Enter CSV file path:")

try:
    # Use the actual uploaded file name, not user_input for pd.read_csv after files.upload()
    # uploaded.keys() returns a list-like object of uploaded filenames
    leads = pd.read_csv(file_name)

    # Rename columns if they don't match expected names
    if "Lead Name" in leads.columns: # Check for 'Lead Name' and rename to 'Name'
        leads.rename(columns={"Lead Name": "Name"}, inplace=True)
    if "Job Title" in leads.columns: # Check for 'Job Title' and rename to 'Title'
        leads.rename(columns={"Job Title": "Title"}, inplace=True)

    if "Name" not in leads.columns or "Title" not in leads.columns:
        raise ValueError("The uploaded CSV must contain 'Name' and 'Title' columns.")
except Exception as e:
    print(f"Error reading CSV or missing required columns: {e}")
    # If there's an error, it's better to stop or handle it gracefully
    # For now, we'll re-raise the exception to prevent further errors
    raise

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

candidate_labels=["Decision Maker", "Individual Contributor"]
classified_tiers=[]
ai_confidence=[] # Initialize ai_confidence here
print("🧠 AI is analyzing lead seniority...")

for title in leads["Title"]:
  print(f"Attempting to classify title: {title}") # Added for better debugging
  try:
    result = classifier(title, candidate_labels)
    tier = result["labels"][0]
    score = result["scores"][0]
    print(f"Processing: {title}") # Original print statement

    # Safety check logic
    if score < 0.80:
       display_tier = f"{tier} (Needs Review)"
    else:
      display_tier = tier
    classified_tiers.append(display_tier) # Move append outside the if-else to ensure it's always called
    ai_confidence.append(f"{score:.2%}")
  except Exception as e:
    print(f"Error during classification for title '{title}': {e}")
    # Depending on desired behavior, you might want to skip this title or re-raise
    raise # Re-raising to ensure the error is fully reported


df=pd.DataFrame({
    "Lead Name": leads["Name"],
    "Job Title": leads["Title"],
    "Tier": classified_tiers,
    "AI_Confidence": ai_confidence
})

df.to_csv("clean_leads.csv", index=False)

# Create the "Urgent" list (only Decision Makers who are NOT flagged for review)
urgent_sales = df[df["Tier"] == "Decision Maker"]

# Create the "Manual Review" list
manual_review = df[df["Tier"].str.contains("Review")]

high_value_df=df[df["Tier"]=="Decision Maker"]
high_value_df.to_csv("urgent_leads.csv", index=False)
manual_review.to_csv("manual_review.csv", index=False)

print(high_value_df)
print(manual_review)
