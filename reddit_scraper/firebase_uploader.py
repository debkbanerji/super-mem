import json
import os
from os import listdir
from os.path import isfile, join

import pyrebase

target_directory = "../sample_meme_files"
image_extensions = ['jpg']


configFile = open('firebase-config.json', 'r+')
config = json.load(configFile)

firebase = pyrebase.initialize_app(config)

db = firebase.database()
memesRef = db.child("memes")

storage = firebase.storage()


def upload_image(path):
    print("Uploading " + path)
    split_path = path.split("/")
    storage.child(split_path[len(split_path) - 1]).put(path)
    # storage.child(path).put(path)

# Uploads all the images in a directory
def upload_images_in_directory(dir_path):
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    directories = [f for f in listdir(dir_path) if not isfile(join(dir_path, f))]
    print(files)
    print(directories)
    for directory in directories:
        upload_images_in_directory(dir_path + "/" + directory)
    for file in files:
        extension_split = file.split(".")
        # if it's an image file
        if (extension_split[len(extension_split) - 1] in image_extensions):
            upload_image(dir_path + "/" + file)

def upload_meme(path):
    split_path = path.split("/")
    fileName = split_path[len(split_path) - 1]
    location, fileName = os.path.split(path)
    print("Uploading " + fileName)
    memesRef.push(fileName)

def upload_memes_in_directory(dir_path):
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    directories = [f for f in listdir(dir_path) if not isfile(join(dir_path, f))]
    # print(files)
    # print(directories)
    for directory in directories:
        upload_memes_in_directory(dir_path + "/" + directory)
    for file in files:
        extension_split = file.split(".")
        # if it's an image file
        if (extension_split[len(extension_split) - 1] == 'meme'):
            upload_meme(dir_path + "/" + file)

upload_memes_in_directory(target_directory)