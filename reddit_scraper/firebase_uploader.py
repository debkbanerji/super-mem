import json
import uuid
import os
import random
from os import listdir
from os.path import isfile, join

import pyrebase

image_extensions = ['jpg']

configFile = open('firebase-config.json', 'r+')
config = json.load(configFile)

firebase = pyrebase.initialize_app(config)

db = firebase.database()

storage = firebase.storage()

#
def upload_image(path, filename):
    print("Uploading " + path)
    split_path = path.split("/")
    storage.child(filename).put(path)
    return storage.child(filename).get_url(None)

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
            print(upload_image(dir_path + "/" + file))

def upload_meme(path):
    location, fileName = os.path.split(path)
    print("Uploading " + path)
    splitFileName = fileName.split(".")

    to_push = fileName

    f = open(path, 'r')
    rawFileData = f.read()

    json_data = json.loads(rawFileData)
    json_data.pop('$id', None)
    json_data.pop('$priority', None)

    to_push = json_data

    # This Version Below Does Not Overwrite Duplicates

    # pushRef = db.child("memes")
    # pushRef.push(to_push)

    # The Version Below Overwrites Duplicates

    pushRef = db.child("memes").child(splitFileName[0])
    pushRef.set(to_push)

def upload_meme_json(json_data, filename):
    json_data.pop('$id', None)
    json_data.pop('$priority', None)

    to_push = json_data

    # This Version Below Does Not Overwrite Duplicates

    # pushRef = db.child("memes")
    # pushRef.push(to_push)

    # The Version Below Overwrites Duplicates

    pushRef = db.child("memes").child(filename)
    pushRef.set(to_push)

def upload_memes_in_directory(dir_path):
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    directories = [f for f in listdir(dir_path) if not isfile(join(dir_path, f))]
    # print(files)
    # print(directories)
    random.shuffle(files)
    random.shuffle(directories)
    for directory in directories:
        upload_memes_in_directory(dir_path + "/" + directory)
    for file in files:
        extension_split = file.split(".")
        # if it's an image file
        if (extension_split[len(extension_split) - 1] == 'meme'):
            upload_meme(dir_path + "/" + file)
