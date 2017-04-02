#!/usr/bin/env python3

from reddit_scraper import scraper, firebase_uploader
from cv import img_decomposition
import tempfile
import shutil
import os
import uuid
import traceback
import pytesseract
from PIL import Image

def go():
    reddit = scraper.RedditScraper()
    all_scraped_files = reddit.scrape_all(['blackpeopletwitter', 'wholesomememes'], 30)
    # all_scraped_files = ['cv/img_test/suit.jpeg']
    # all_scraped_files = [de.path for de in os.scandir('output/wholesomememes/')]

    num_failures = 0
    memento = {}
    for img_path in all_scraped_files:
        base_filename = str(uuid.uuid1())
        container_folder = tempfile.mkdtemp(prefix="img_decomp_")
        print('image decomp for %s generating in %s' % (img_path, container_folder))
        try:
            processed_image = img_decomposition.decompose_image(img_path, container_folder)
            objects_to_process = processed_image.decomp_objects
            for ocr_img_obj in objects_to_process:
                if ocr_img_obj.type == img_decomposition.TYPE_TEXT:
                    ocr_img_obj.data = pytesseract.image_to_string(Image.open(ocr_img_obj.file_path))
                else:
                    firebase_url = upload_image(base_filename, ocr_img_obj.file_path)
                    ocr_img_obj.data = firebase_url


            # upload metadata for hackathon
            contours_vis_url = upload_image(base_filename, processed_image.regions_map_vis)
            original_graphic_url = upload_image(base_filename, processed_image.original_file_path)
            processed_image.regions_map_vis = contours_vis_url
            processed_image.original_file_path = original_graphic_url

            meme_dict = processed_image.__dict__()
            firebase_uploader.upload_meme_json(meme_dict, base_filename)

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            shutil.rmtree(container_folder)
            num_failures += 1

    print("TOTAL ATTEMPTED:", len(all_scraped_files))
    print("FAILURE RATE: ", num_failures)


def upload_image(base_filename, file_path):
    result = firebase_uploader.upload_image(file_path, base_filename + '_' + os.path.basename(file_path))
    print('uploaded to', result)
    return result

go()

