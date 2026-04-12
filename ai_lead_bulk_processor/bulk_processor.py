"""
Project: AI Lead Bulk Processor

Description:
Processes large lead datasets and classifies them into decision-makers
and contributors using AI, with confidence scoring and review flags.
"""
import pandas as pd
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

leads = {
    "Name": ["James Cook", "Amy Lin", "Robert Fox", "Sara Sun", "Kevin Hart", "Alice Green", "Tom Riddle", "Sarah Jenkins", "Bruce Wayne", "Clark Kent"],
    "Title": ["CEO & Founder", "Junior Graphic Designer", "Director of Operations", "Intern", "Receptionist", "VP of Sales", "Data Entry Clerk", "Managing Director", "Owner", "Staff Accountant"]
}
candidate_labels=["Decision Maker", "Individual Contributor"]
classified_tiers=[]
ai_confidence=[] # Initialize ai_confidence here
print("🧠 AI is analyzing lead seniority...")

for title in leads["Title"]:
  result = classifier(title, candidate_labels)
  tier = result["labels"][0]
  score = result["scores"][0]
  print(f"Processing: {title}")
  
  # Safety check logic
  if score < 0.80:
     display_tier = f"{tier} (Needs Review)"
  else:
    display_tier = tier
  classified_tiers.append(display_tier) # Move append outside the if-else to ensure it's always called
  ai_confidence.append(f"{score:.2%}")


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
