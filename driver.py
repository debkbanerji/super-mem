#!/usr/bin/env python3

from reddit_scraper import scraper
from cv import img_decomposition
import tempfile
import shutil
import os
import traceback

reddit = scraper.RedditScraper()
# all_scraped_files = reddit.scrape_all(['wholesomememes'], 30)
all_scraped_files = ['cv/img_test/suit.jpeg']
# all_scraped_files = [de.path for de in os.scandir('output/wholesomememes/')]
for img_path in all_scraped_files:
    container_folder = tempfile.mkdtemp(prefix="img_decomp_")
    print('image decomp for %s generating in %s' % (img_path, container_folder))
    try:
        objects_to_process = img_decomposition.decompose_image(img_path, container_folder)
    except TypeError as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        shutil.rmtree(container_folder)
