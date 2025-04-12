# -*- coding: utf-8 -*-

from openai import OpenAI
from datetime import datetime
import glob
import os
import re
import json
import time
import threading


#make string to json
def parse_post_data(post_text):
    post_data = {}
    fields = [
        "Title", "Body", "Sentiment",
        "Key topics or keywords", "Suggested marketing tags",
        "Engagement metrics", "Actionable insights or marketing recommendations"
    ]

    for field in fields:
        pattern = rf"{field}:\s*(.*?)(?=\n[A-Z]|$)"
        match = re.search(pattern, post_text, re.DOTALL)
        if match:
            post_data[field] = match.group(1).strip()
        else:
            post_data[field] = None

    return post_data

def text_combiner(file_name):
    combined_texts = []
    raw_files = glob.glob(f"{file_name}*.txt")
    for raw_file in raw_files:
        with open(raw_file, 'r', encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    combined_texts.append(stripped)
    return combined_texts

#Split post by post
def text_spilter(text):
    posts = text.split("eeeennnndddd")
    return posts

# Upstage AI 클라이언트 설정
client = OpenAI(
    api_key="up_a7XoezShuK96mgukxl3fwu0KVDe7J",
    base_url="https://api.upstage.ai/v1"
)

file_name = "reddit_hot_comments_"
comments = text_combiner(file_name)
comments = ".\n".join(comments)
eachPost = text_spilter(comments)

print(f"------------{len(eachPost)}")
print()
result = []
i = 1
for post in eachPost:
    try:
        
        # AI 요청 생성 (마케팅 목적에 맞게 데이터 요청)
        response = client.chat.completions.create(
            model="solar-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured marketing data from Reddit posts. "
                               "You can analyze sentiment, extract key topics, and provide actionable insights for marketing purposes."
                },
                {
                    "role": "user",
                    "content": f"""Here is a Reddit post:

                    {post}

                    Please extract and return a single JSON object with the following keys:

                    - Title
                    - Creation Time  
                    - Body  
                    - Sentiment (Positive, Negative, Neutral)  
                    - Key topics or keywords  
                    - Suggested marketing tags (e.g. 'Product', 'Service', 'Marketing')  
                    - top 3 comments and comment sentiment
                    - Actionable insights or marketing recommendations based on the post content

                    Return only **one valid JSON object**, no explanations or additional text."""
                }

            ],
            temperature=0.7
        )

        # AI 응답 받기
        extracted_data = response.choices[0].message.content.strip()
        #test----------------------
        #print("===RAW RESPONSE===")
        #print(extracted_data)
        print(i)
        i += 1
        parsed = json.loads(extracted_data)
        #---------------------------
        #parsed = parse_post_data(extracted_data)
        result.append(parsed)

        #time.sleep(0)

    except Exception as e:
        print(f"Error processing post: {post}\nError: {e}")

now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
f = open(f"extracted_{now}.json", 'w',encoding="utf-8")

json.dump(result,f, ensure_ascii=False, indent=4)

f.close()

