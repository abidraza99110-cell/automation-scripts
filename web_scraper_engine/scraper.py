import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline

all_scraped_data = []

for page in range(1, 4):  # To load pages from 1 to 3
    url = f"http://books.toscrape.com/catalogue/page-{page}.html"
    print(f"📡 Scraping Page {page}...")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all('article', class_='product_pod')

    for book in books:
        title = book.h3.a['title']
        raw_price_str = book.find('p', class_='price_color').text # Renamed to avoid confusion with column name
        clean_price = float(raw_price_str.replace('Â', '').replace('£', ''))

        if clean_price < 12.00:
            status = "CHEAP"
        else:
            status = "EXPENSIVE"

        # Append to the big list
        all_scraped_data.append({"Title": title, "Price": clean_price, "Status": status})

# After the big loop finishes, THEN make the DataFrame
df = pd.DataFrame(all_scraped_data)

Average_price = df["Price"].mean()
Most_expensive = df["Price"].max()
Mininum_price = df["Price"].min()
total_books = len(df)
print("Average Price:", Average_price)
print("Most Expensive Price:", Most_expensive)
print("Minimum Price:", Mininum_price)
print("Total Books:", total_books)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

candidate_labels = ["Expensive Market", "Budget Friendly Market"]

# Apply the classifier to the book titles to get market sentiment
market_sentiments = []
for title_text in df["Title"]:
    # The zero-shot classifier returns a dictionary, we want the best label
    classification_result = classifier(title_text, candidate_labels)
    market_sentiments.append(classification_result["labels"][0])

df["Market_Sentiment"] = market_sentiments

df.to_csv("Market_sentiment.csv", index=False)
print("Saved market sentiment to Market_sentiment.csv!")
