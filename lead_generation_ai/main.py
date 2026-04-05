import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline

# 1. Scraper Setup
url = "https://remoteok.com/remote-engineer-jobs"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
leads_data = []

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = soup.find_all('tr', class_='job')

    for job in jobs[:10]:
        title_el = job.find('h2', itemprop='title')
        comp_el = job.find('h3', itemprop='name')
        if title_el and comp_el:
            leads_data.append({"Company": comp_el.text.strip(), "Role": title_el.text.strip()})
except:
    print("📡 Connection failed or blocked. Switching to Backup Data...")

# --- THE BACKUP (Ensures you graduate even if blocked!) ---
if not leads_data:
    print("⚠️ Website blocked the request. Using 'Mock Leads' to demonstrate the AI...")
    leads_data = [
        {"Company": "Stripe", "Role": "Senior Staff Engineer"},
        {"Company": "Airbnb", "Role": "Junior Frontend Developer"},
        {"Company": "Tesla", "Role": "VP of Engineering"},
        {"Company": "Shopify", "Role": "Lead Data Scientist"},
        {"Company": "Google", "Role": "Level 3 Software Engineer"}
    ]

# 2. AI Classification Logic
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ["Decision Maker", "Individual Contributor"]
final_results = []
scores = []

for lead in leads_data:
    res = classifier(lead["Role"], candidate_labels)
    tier = res["labels"][0]
    conf = res["scores"][0]

    # Professional Email Logic
    if tier == "Decision Maker" and conf > 0.80:
        email = f"Dear {lead['Company']} Leadership, we specialize in scaling {lead['Role']} workflows."
    else:
        email = f"Hi {lead['Company']} Team, I have a tool to help your {lead['Role']} work faster."

    final_results.append({
        "Company": lead['Company'],
        "Role": lead['Role'],
        "Tier": tier,
        "Confidence": f"{conf:.2%}",
        "Email": email
    })
    scores.append(conf)

# 3. Final Summary Report
avg_conf = sum(scores) / len(scores)
print("\n" + "="*40)
print(f"🎓 MASTER ANALYSIS COMPLETE")
print(f"Average AI Confidence: {avg_conf:.2%}")
print("="*40)

df_final = pd.DataFrame(final_results)
df_final.to_csv("graduation_leads.csv", index=False)
print(df_final[['Company', 'Role', 'Tier', 'Confidence']])
