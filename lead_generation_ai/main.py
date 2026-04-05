import requests
import pandas as pd
from transformers import pipeline
import time

# ==============================
# 1. FETCH DATA (API METHOD)
# ==============================
def fetch_jobs():
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        jobs = []
        # API returns a list, with the first element being metadata.
        # We iterate from the second element onwards.
        for job in data[1:15]:
          company=job.get("company", "Unknown")
          position=job.get("position", "Unknown")
          jobs.append({"Company": company, "Role": position})
        return jobs
    except Exception as e:
        print(f"❌ API failed: {e}. Using backup data.")
        return [
            {"Company": "Stripe", "Role": "Senior Staff Engineer"},
            {"Company": "Airbnb", "Role": "Junior Frontend Developer"},
            {"Company": "Tesla", "Role": "VP of Engineering"},
            {"Company": "Shopify", "Role": "Lead Data Scientist"},
            {"Company": "Google", "Role": "Level 3 Software Engineer"}
        ]

def filter_niche(leads_list):
    # Professional keyword list to catch all technical roles
    tech_keywords = ["engineer", "developer", "scientist", "programmer", "tech", "devops"]
    filtered_leads = []
    
    for lead in leads_list:
        role = lead["Role"].lower()
        if any(keyword in role for keyword in tech_keywords):
            filtered_leads.append(lead)
            
    return filtered_leads

# ==============================
# 2. AI CLASSIFIER
# ==============================
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = ["Decision Maker", "Individual Contributor"]

def classify_role(role):
    result = classifier(role, labels)
    return result["labels"][0], result["scores"][0]


# =============================
# 3. LEAD SCORING SYSTEM
# =============================
def score_lead(role, confidence):
    senior_keywords = ["VP", "Head", "Director", "Lead", "Chief"]

    score = 0

    if any(word.lower() in role.lower() for word in senior_keywords):
        score += 50

    score += confidence * 50

    return round(score, 2)


# ==============================
# 4. EMAIL GENERATOR
# ==============================
def generate_email(company, role, tier):

    if tier == "Decision Maker":
        return f"""Subject: Helping {company} scale faster\n\nDear {company} Leadership,\n\nI noticed you're hiring for {role}.\nWe help companies streamline engineering workflows and improve team productivity.\n\nWould you be open to a quick discussion?\n\nBest regards,\n[Your Name]\n"""
    else:
        return f"""Subject: Tool to boost your {role} productivity\n\nHi {company} Team,\n\nI came across your opening for {role}.\nI’ve built a tool that helps developers work faster and reduce repetitive tasks.\n\nHappy to share more if you're interested.\n\nBest,\n[Your Name]\n"""


# ==============================
# 5. MAIN PIPELINE
# ==============================
def main():
    initial_leads = fetch_jobs()
    leads = filter_niche(initial_leads) # Filter the fetched leads

    results = []
    confidences = []

    print("⚙️ Processing leads...\n")

    if not leads:
        print("No leads found after filtering. Exiting.")
        return

    for lead in leads:
        role = lead["Role"]
        company = lead["Company"]

        tier, conf = classify_role(role)
        score = score_lead(role, conf)
        email = generate_email(company, role, tier)

        results.append({
            "Company": company,
            "Role": role,
            "Tier": tier,
            "Confidence": f"{conf:.2%}",
            "Score": score,
            "Email": email
        })

        confidences.append(conf)
        time.sleep(1)  # avoid overload

    # Summary
    avg_conf = sum(confidences) / len(confidences)

    print("="*50)
    print("🎓 LEAD GENERATION REPORT")
    print(f"Average AI Confidence: {avg_conf:.2%}")
    print("="*50)

    df = pd.DataFrame(results)
    df = df.sort_values(by="Score", ascending=False)

    df.to_csv("ai_leads_output.csv", index=False)

    print(df[["Company", "Role", "Tier", "Score"]])


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    main()
  
