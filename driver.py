#!/usr/bin/env python3

from reddit_scraper import scraper
from cv import img_decomposition
import tempfile
import shutil
import os
import traceback
import pytesseract
from PIL import Image

reddit = scraper.RedditScraper()
# all_scraped_files = reddit.scrape_all(['wholesomememes'], 30)
all_scraped_files = ['cv/img_test/suit.jpeg']
# all_scraped_files = [de.path for de in os.scandir('output/wholesomememes/')]
for img_path in all_scraped_files:
    container_folder = tempfile.mkdtemp(prefix="img_decomp_")
    print('image decomp for %s generating in %s' % (img_path, container_folder))
    try:
        objects_to_process = img_decomposition.decompose_image(img_path, container_folder)
        # print(objects_to_process)
        for ocr_img_obj in objects_to_process:
            if ocr_img_obj.type == img_decomposition.TYPE_TEXT:
                ocr_img_obj.data = pytesseract.image_to_string(Image.open(ocr_img_obj.file_path))
            else:
                pass
                # TODO NEED firebase upload and resource indicator add to ocr_img_obj.data!

    except TypeError as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        shutil.rmtree(container_folder)
