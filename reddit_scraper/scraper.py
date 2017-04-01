import json
git puimport os

import praw
import urllib.request

subreddits = ["wholesomememes"]
max_per_subreddit = 4
output_folder = "output"

check_words = ['jpg']

credFile = open('credentials.json', 'r+')
credentials = json.load(credFile)
CLIENT_ID = credentials["client_id"]
CLIENT_SECRET = credentials["client_secret"]

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent='test')

if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def scrape_subreddit(subreddit):
    print("Scraping memes from r/" + subreddit)
    if not os.path.exists(output_folder + "/" + subreddit):
        os.makedirs(output_folder + "/" + subreddit)
    for submission in reddit.subreddit(subreddit).hot(limit=max_per_subreddit):
        is_image = any(string in submission.url for string in check_words)
        # print ('[LOG] Checking url:  ' + submission.url)
        # print(submission.shortlink)
        if is_image:
            image_url = submission.url
            # print(image_url)
            split_string = image_url.split("/")

            f = open(output_folder + "/" + subreddit + "/" + split_string[len(split_string) - 1], 'wb')
            f.write(urllib.request.urlopen(image_url).read())
            f.close()


for subreddit in subreddits:
    try:
        scrape_subreddit(subreddit)
    except:
        print("Error scraping r/" + subreddit)
    print("Done")
