# -*- coding: utf-8 -*-

from Extractor import Extractor
from RedditCrawler import RedditCrawler
from openai import OpenAI
import json

def get_recommended_subreddits_upstage(topic, num=5):
    client = OpenAI(
        api_key="~~~~~~~",
        base_url="~~~~~~"
    )

    prompt = f"""
I'm planning a marketing campaign about: "{topic}".

Please suggest {num} of the most relevant and active subreddits (just the names, no /r/) where users are discussing this topic.

Return ONLY a JSON array (e.g. ["CryptoCurrency", "Bitcoin", "ethdev"]) with no explanation, no extra text, and no formatting. The output must be a valid JSON array.
"""

    try:
        response = client.chat.completions.create(
            model="solar-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that recommends subreddit names for a given marketing topic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        content = response.choices[0].message.content.strip()
        subreddits = json.loads(content)  # ← JSON 리스트로 파싱
        return subreddits

    except Exception as e:
        print(f"[ERROR] Subreddit recommandation fail: {e}")
        return []

def autoCrawling(sub):
    reddit = RedditCrawler(
        id="~~~~~~~",
        secret="~~~~~~~~",
        username="~~~~~~~~",       
        password="~~~~~~~",
        subReddit= sub,  
        searchsize=100
    )
    reddit.run_all()

    ex = Extractor(sub,
                   "~~~~~~~",
                   "~~~~~~~", 30)


    ex.run_all()

text = input("What kinds of Marketing do you want?     ")
subreddits = get_recommended_subreddits_upstage(text, num = 5)
print(subreddits)


for sub in subreddits:
    autoCrawling(sub)
    print(f"Task {sub} is done \n")