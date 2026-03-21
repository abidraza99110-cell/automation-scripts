import requests
from bs4 import BeautifulSoup
import pandas as pd # Import pandas

url = "http://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
books = soup.find_all('article', class_='product_pod')

# 1. Create an empty list to store our data
data = []

for book in books:
    title = book.h3.a['title']
    price = book.find('p', class_='price_color').text

    # 2. Append each book as a dictionary to our list
    data.append({
        "Title": title,
        "Price": price
    })

# 3. Convert the list to a Pandas DataFrame
df = pd.DataFrame(data)

# 4. Export to CSV
df.to_csv("book_prices.csv", index=False)
print("Saved 20 books to book_prices.csv!")
