# -*- coding: utf-8 -*-

from openai import OpenAI
from datetime import datetime
import glob
import os
import re
import json
import time
import threading

#define max semaphore
MAX_CONCURRENT_THREADS = 10
semaphore = threading.Semaphore(MAX_CONCURRENT_THREADS)

#to multi thread
class ExtractThread(threading.Thread):
    def __init__(self, id, post, name=None):
        super().__init__(name=name)
        self.id = id
        self.data = post
    
    def run(self):
        with semaphore:
            print(f"Thread {self.name} ({self.id}) is running")
            self.result = self.extract()

    def extract(self):
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
                    - Body  
                    - Sentiment (Positive, Negative, Neutral)  
                    - Key topics or keywords  
                    - Suggested marketing tags (e.g. 'Product', 'Service', 'Marketing')  
                    - Engagement metrics (e.g. upvotes, downvotes, comments)  
                    - Actionable insights or marketing recommendations based on the post content

                    Return only **one valid JSON object**, no explanations or additional text."""
                    }

                ],
                temperature=0.7
            )

        # AI 응답 받기
            extracted_data = response.choices[0].message.content.strip()
            return extracted_data
        
        except Exception as e:
            print(f"Error processing post: {post}\nError: {e}")

            #if 'too_many_requests' in str(e):
                #time.sleep()
                #return self.extract()

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

threads = []
result = []

#Start multi Threading
for i,post in enumerate(eachPost):
    
    thread = ExtractThread(i,post, "IO")
    extracted_data = thread.start()
    threads.append(thread)
    

#wait to child
for thread in threads:
    thread.join()
    extracted_data = thread.result

    if extracted_data:
        try:
            parsed = json.loads(extracted_data)
            result.append(parsed)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
f = open(f"extracted_{now}.json", 'w',encoding="utf-8")

json.dump(result,f, ensure_ascii=False, indent=4)

f.close()

