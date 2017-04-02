#!/usr/bin/env python3

from reddit_scraper import scraper, firebase_uploader
from cv import img_decomposition
import tempfile
import shutil
import os
import traceback
import pytesseract
from PIL import Image

def go():
    reddit = scraper.RedditScraper()
    # all_scraped_files = reddit.scrape_all(['wholesomememes'], 30)
    all_scraped_files = ['cv/img_test/suit.jpeg']
    # all_scraped_files = [de.path for de in os.scandir('output/wholesomememes/')]

    num_failures = 0
    memento = {}
    for img_path in all_scraped_files:
        container_folder = tempfile.mkdtemp(prefix="img_decomp_")
        print('image decomp for %s generating in %s' % (img_path, container_folder))
        try:
            objects_to_process, img_width, img_height = img_decomposition.decompose_image(img_path, container_folder)
            for ocr_img_obj in objects_to_process:
                if ocr_img_obj.type == img_decomposition.TYPE_TEXT:
                    ocr_img_obj.data = pytesseract.image_to_string(Image.open(ocr_img_obj.file_path))
                else:
                    firebase_url = firebase_uploader.upload_image(ocr_img_obj.file_path)
                    ocr_img_obj.data = firebase_url

            meme_dict = make_enclosing_json(img_width, img_height, objects_to_process)
            print(meme_dict)
            firebase_uploader.upload_meme_json(meme_dict)

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            shutil.rmtree(container_folder)
            num_failures += 1

    print("TOTAL ATTEMPTED:", len(all_scraped_files))
    print("FAILURE RATE: ", num_failures)

def make_enclosing_json(img_width, img_height, subcomponents):
    objects = {}
    for i in range(len(subcomponents)):
        obj = subcomponents[i]
        objects['obj' + str(i)] = obj.__dict__()

    json_map = {
        'width': img_width,
        'height': img_height,
        'objects': objects
    }
    return json_map

go()

