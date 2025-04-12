# -*- coding: utf-8 -*-

from openai import OpenAI
from datetime import datetime
import glob
import os
import re
import json
import time
import threading


class Extractor:
    def __init__(self, file_name_prefix, api_key, base_url, max_threads = 10):
        self.file_name_prefix = file_name_prefix
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.max_threads = max_threads
        self.semaphore = threading.Semaphore(max_threads)
        self.posts = []
        self.result = []

    #load data from "file_name_prefix"
    def load_data(self):
        combined_texts = []
        raw_files = glob.glob(f"{self.file_name_prefix}.txt")
        for raw_file in raw_files:
            with open(raw_file, 'r', encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        combined_texts.append(stripped)
        joined_text = ".\n".join(combined_texts)
        self.posts = joined_text.split("-----")

    #Thread for Extract
    class ExtractThread(threading.Thread):
        def __init__(self, id, post, client, semaphore, name=None):
            super().__init__(name=name)
            self.id = id
            self.post = post
            self.client = client
            self.semaphore = semaphore
            self.result = None

        def run(self):
            with self.semaphore:
                print(f"Thread {self.name} ({self.id}) is running")
                self.result = self.extract()
        #using upStage ai to summariaze "important data"
        def extract(self):
            try:
                response = self.client.chat.completions.create(
                    model="solar-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that extracts structured marketing data from Reddit posts."
                        },
                        {
                            "role": "user",
                            "content": f"""Here is a Reddit post:

                            {self.post}

                            Please extract and return a single JSON object with the following keys:

                            - Title
                            - Creation-Time  
                            - Body  
                            - Sentiment
                            - Key-topics-or-keywords  
                            - Suggested-marketing-tags
                            - Top-3-comments
                            - comment-sentiment
                            **Return only subreddit names that actually exist on Reddit.** 
                            Return only **one valid JSON object**, no explanations or additional text."""
                        }
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"[ERROR] Post ID {self.id} | Error: {e}")
                return None
            
    #Do multithreading        
    def process_posts(self):
        threads = []
        for i, post in enumerate(self.posts):
            thread = self.ExtractThread(i, post, self.client, self.semaphore, name=f"Thread-{i}")
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
            if thread.result:
                try:
                    parsed = json.loads(thread.result)
                    self.result.append(parsed)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

    def save_results(self):
        
        now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        with open(f"extracted_{self.file_name_prefix}.json", 'w', encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)
    
    def run_all(self):
        self.load_data()
        print(f"[INFO] Total posts: {len(self.posts)}")
        self.process_posts()
        self.save_results() 


#example
"""
ex = Extractor("reddit_hot_comments_","~~~~~~","~~~~~", 30)
Extractor(file_name, your_api_key, your_base_url)
and just execute run_all()
ex.run_all()
"""
