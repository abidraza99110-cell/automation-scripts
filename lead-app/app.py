import streamlit as st
import pandas as pd
import requests 
import time     

# ==============================
# Page Config
# ==============================
st.set_page_config(page_title="AI Lead Classification Tool", layout="wide")

st.title("🧠AI sales automation tool")
st.write("Upload your CSV file with lead 'Name' and 'Title' columns to classify them.")

# ==============================
# Heuristic Classification Logic 
# ==============================

# Define keywords for classification
DECISION_MAKER_KEYWORDS = ["ceo", "cto", "cfo", "director", "vp", "president", "head of", "founder", "owner", "partner"]
STRONG_DM_KEYWORDS = ["ceo", "cto", "cfo", "vp", "director", "founder", "president"]
INDIVIDUAL_CONTRIBUTOR_KEYWORDS = ["engineer", "developer", "specialist", "analyst", "associate", "intern", "staff", "representative"]

def classify_role_heuristic(title_text):
    """Classifies a job title as 'Decision Maker' or 'Individual Contributor' using keyword matching.
       Assigns a heuristic confidence score based on keyword strength.
    """
    title_text_lower = title_text.lower()

    # Prioritize strong decision maker keywords
    if any(keyword in title_text_lower for keyword in STRONG_DM_KEYWORDS):
        return "Decision Maker", 0.98

    # Check for other decision maker keywords
    if any(keyword in title_text_lower for keyword in DECISION_MAKER_KEYWORDS):
        return "Decision Maker", 0.90

    # Handle 'manager' and 'lead' with nuanced confidence
    if "manager" in title_text_lower:
        # If "manager" is combined with a senior role indicator, lean DM
        if any(k in title_text_lower for k in ["senior manager", "group manager", "department manager"]):
            return "Decision Maker", 0.75 # Moderate DM confidence, might trigger review
        return "Individual Contributor", 0.65 # Default manager to IC, moderate confidence

    if "lead" in title_text_lower:
        # "Lead Engineer" is IC, "Lead of Department" is DM. Assume IC unless other DM keywords.
        if any(k in title_text_lower for k in ["lead of", "lead manager", "lead, "]):
            return "Decision Maker", 0.70 # Moderate DM confidence, might trigger review
        return "Individual Contributor", 0.60 # Default lead to IC, moderate confidence

    # Check for individual contributor keywords (after ambiguous roles for better DM detection)
    if any(keyword in title_text_lower for keyword in INDIVIDUAL_CONTRIBUTOR_KEYWORDS):
        return "Individual Contributor", 0.95

    # If no specific keywords are found
    return "Individual Contributor", 0.50 # Default to IC with low confidence for review

# ==============================
# File Upload
# ==============================
uploaded_file = st.file_uploader("Upload CSV file (must contain 'Name' and 'Title' columns)", type=["csv"])

if uploaded_file:
    try:
        leads_df = pd.read_csv(uploaded_file)

        # Ensure required columns exist and rename if necessary
        if "Lead Name" in leads_df.columns:
            leads_df.rename(columns={"Lead Name": "Name"}, inplace=True)
        if "Job Title" in leads_df.columns:
            leads_df.rename(columns={"Job Title": "Title"}, inplace=True)

        if "Name" not in leads_df.columns or "Title" not in leads_df.columns:
            st.error("The uploaded CSV must contain 'Name' and 'Title' columns.")
            st.stop()

        st.subheader("📊 Raw Data Preview")
        st.dataframe(leads_df.head())

        if st.button("🚀 Process Leads"): # Use a button to trigger processing
            classified_tiers = []
            ai_confidence = []

            st.write("🧠 AI is analyzing lead seniority using a keyword-based heuristic...")
            leads_df["Title"] = leads_df["Title"].fillna("Unknown") # Handle missing titles

            progress_bar = st.progress(0)
            total_leads = len(leads_df)

            for index, row in leads_df.iterrows():
                title = str(row["Title"]).strip() # Ensure title is string and clean whitespace

                # Apply the heuristic classification
                tier, score = classify_role_heuristic(title)

                # Safety check logic (from original code, adapted for heuristic score)
                display_tier = tier
                # Threshold for flagging for review (from original code example)
                if score < 0.80:
                   display_tier = f"{tier} (Needs Review)"

                classified_tiers.append(display_tier)
                ai_confidence.append(f"{score:.2%}")
                progress_bar.progress((index + 1) / total_leads)

            leads_df["Tier"] = classified_tiers
            leads_df["AI_Confidence"] = ai_confidence

            st.subheader("✅ Processed Leads")
            st.dataframe(leads_df)

            # Create the "Urgent" list (only Decision Makers who are NOT flagged for review)
            # Adjusted logic to filter based on the 'Tier' column after processing
            urgent_sales = leads_df[
                (leads_df["Tier"] == "Decision Maker")
            ]

            # Create the "Manual Review" list
            manual_review = leads_df[leads_df["Tier"].str.contains("(Needs Review)")]

            st.subheader("🔥 High-Value Leads (Decision Makers)")
            if not urgent_sales.empty:
                st.dataframe(urgent_sales)
                st.download_button(
                    label="Download High-Value Leads CSV",
                    data=urgent_sales.to_csv(index=False).encode("utf-8"),
                    file_name="urgent_leads.csv",
                    mime="text/csv",
                )
            else:
                st.info("No high-value leads found without requiring review.")


            st.subheader("⚠️ Leads for Manual Review")
            if not manual_review.empty:
                st.dataframe(manual_review)
                st.download_button(
                    label="Download Manual Review Leads CSV",
                    data=manual_review.to_csv(index=False).encode("utf-8"),
                    file_name="manual_review.csv",
                    mime="text/csv",
                )
            else:
                st.info("No leads flagged for manual review.")

            st.download_button(
                label="Download All Processed Leads CSV",
                data=leads_df.to_csv(index=False).encode("utf-8"),
                file_name="clean_leads.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"An error occurred during file processing: {e}")
        st.exception(e)
