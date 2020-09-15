"""Place the zips in one location and run this script to recursively unzip everything"""
import zipfile
import os

data_location = '../data/'


def search_and_unzip(location):
    list_dir = os.listdir(location)
    print(f'Searching for zips in {location}...')

    for item in list_dir:
        if zipfile.is_zipfile(location + item):
            print(f'Found zip: {location + item}')
            with zipfile.ZipFile(location + item, 'r') as zipObj:
                zipObj.extractall(location)
                # os.remove(location + item)

    list_dir = os.listdir(location)
    for item in list_dir:
        if os.path.isdir(location + item):
            search_and_unzip(f'{location}{item}/')


search_and_unzip(data_location)
