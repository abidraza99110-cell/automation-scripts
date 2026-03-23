from transformers import pipeline
import pandas as pd

import pandas as pd
from transformers import pipeline

df = pd.read_csv("/content/file.csv.txt")

summarizer = pipeline("summarization", model="t5-small")

data = []

for text in df["Long_Description"]:
    summary = summarizer(text, max_length=60, min_length=20, do_sample=False)
    data.append(summary[0]["summary_text"])

print(data)
