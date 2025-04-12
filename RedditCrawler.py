# -*- coding: utf-8 -*-
import praw
from datetime import datetime
import textwrap
import threading
import re
import threading


class RedditCrawler:
    def __init__(self, id, secret, username, password, subReddit, searchsize = 100):
        self.id = id
        self.secret = secret
        self.username = username
        self.password = password
        self.subReddit = subReddit
        self.searchsize = searchsize
        
    #Connect to Reddit
    def init_reddit(self):
        reddit = praw.Reddit(
            client_id= self.id,
            client_secret= self.secret,
            user_agent="bluecat",
            username=self.username,       
            password= self.password
        )
        self.reddit = reddit
    
    #remove unuseful text
    def clean_text(self,text):
        text = text.replace('\n', ' ').strip()
        text = re.sub(r"[^a-zA-Z0-9.,!?\'\"()\-:; ]", "", text)
        return text
    
    def save_crawl_data(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        searchSize = self.searchsize
        subreddit = self.reddit.subreddit(self.subReddit)
        f = open(f"{self.subReddit}" + ".txt" , 'w', encoding = 'utf-8')

        f.write("Record Start Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
        for i,post in enumerate(subreddit.hot(limit = searchSize), start = 1):
            f.write(f"\n\nPost {i}:\n")
    
            #print post number
            print(i)

            #write repost
            created_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"Creation Time at (UTC): {created_time}\n")
            f.write(f"Title: {self.clean_text(post.title)}\n")
            wrapped_body = textwrap.fill(self.clean_text(post.selftext), width = 80)
            f.write(f"Body:{wrapped_body}\n")
            #f.write(f"URL: {post.url}\n")
            f.write("Comments:\n")

            post.comments.replace_more(limit=0)
            for comment in post.comments[:3]:
                cleaned_comment = self.clean_text(comment.body)
                #cleaned_comment = comment.body.replace('\n', ' ').strip()
                f.write(f"- {cleaned_comment}\n")
            f.write("-----")

        f.write("\nRecord End Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.close()

    def run_all(self):
        self.init_reddit()
        self.save_crawl_data()

        print("complete save text")

#example
"""reddit = RedditCrawler(
    id="~~~~~~~~",
    secret="~~~~~",
    username="~~~~~~",       
    password="~~~~~~",
    subReddit="baseball",  
    searchsize=100
)
reddit.run_all()
"""
