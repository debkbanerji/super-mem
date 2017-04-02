#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

import praw
import urllib.request

class RedditScraper():
    def __init__(self, output_folder="output"):
            self.check_words = ['jpg']
            self.output_folder = output_folder

            credFile = open('credentials.json', 'r+')
            credentials = json.load(credFile)
            CLIENT_ID = credentials["client_id"]
            CLIENT_SECRET = credentials["client_secret"]

            self.reddit = praw.Reddit(client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 user_agent='test')


    def scrape_subreddit(self, subreddit, max_posts):
        filenames = []
        print("Scraping memes from r/" + subreddit)
        if not os.path.exists(self.output_folder + "/" + subreddit):
            os.makedirs(self.output_folder + "/" + subreddit)
        for submission in self.reddit.subreddit(subreddit).hot(limit=max_posts):
            is_image = any(string in submission.url for string in self.check_words)
            # print ('[LOG] Checking url:  ' + submission.url)
            # print(submission.shortlink)
            if is_image:
                image_url = submission.url
                # print(image_url)
                split_string = image_url.split("/")
                file_out = self.output_folder + "/" + subreddit + "/" + split_string[len(split_string) - 1]

                f = open(file_out, 'wb')
                f.write(urllib.request.urlopen(image_url).read())
                f.close()
                filenames.append(file_out)
        return filenames


    def scrape_all(self, subreddits, max_posts):
        all_filenames = []
        for subreddit in subreddits:
            try:
                all_filenames.extend(self.scrape_subreddit(subreddit, max_posts))
            except Exception as e:
                print("Error scraping r/" + subreddit)
                print(e)
            print("Done")
        return all_filenames
