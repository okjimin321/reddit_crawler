# -*- coding: utf-8 -*-
import praw
from datetime import datetime
import textwrap
import threading
import re


def clean_text(text):
    # 줄바꿈 제거
    text = text.replace('\n', ' ').strip()
    # 영어, 숫자, 일반적인 구두점만 남기기 (이외는 제거)
    text = re.sub(r"[^a-zA-Z0-9.,!?\'\"()\-:; ]", "", text)
    return text

# Reddit infor  
reddit = praw.Reddit(
    client_id="_8SGtgdhCTt0LmiZAAupnA",
    client_secret="TA1TOqLehetiygfNMboyp-ZxN4nMWQ",
    user_agent="zzz okjimin",
    username="TurbulentDream6933",       
    password="Ok75792000"
)

#Hot post in "CryptoMarkets"
now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
searchSize = 500
subreddit = reddit.subreddit("CryptoMarkets")
f = open("reddit_hot_comments_" + now + ".txt" , 'w', encoding = 'utf-8')

f.write("Record Start Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
for i,post in enumerate(subreddit.hot(limit = searchSize), start = 1):
    f.write(f"\n\nPost {i}:\n")
    
    #print post number
    print(i)

    #write repost
    created_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
    f.write(f"Creation Time at (UTC): {created_time}\n")
    f.write(f"Title: {clean_text(post.title)}\n")
    wrapped_body = textwrap.fill(clean_text(post.selftext), width = 80)
    f.write(f"Body:{wrapped_body}\n")
    #f.write(f"URL: {post.url}\n")
    f.write("Comments:\n")

    post.comments.replace_more(limit=0)
    for comment in post.comments[:3]:
        cleaned_comment = clean_text(comment.body)
        #cleaned_comment = comment.body.replace('\n', ' ').strip()
        f.write(f"- {cleaned_comment}\n")
    f.write("-----")

f.write("\nRecord End Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
f.close()

