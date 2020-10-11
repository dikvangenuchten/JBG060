"""Place the zips in one location and run this script to recursively unzip everything"""
import zipfile
import os


def search_and_unzip(location):
    list_dir = os.listdir(location)

    for item in list_dir:
        file_path = os.path.join(location, item)
        if zipfile.is_zipfile(file_path):
            print(f'Found zip: {file_path}')
            with zipfile.ZipFile(file_path, 'r') as zipObj:
                zipObj.extractall(location)
                # os.remove(location + item)

    list_dir = os.listdir(location)
    for item in list_dir:
        file_path = os.path.join(location, item)
        if os.path.isdir(file_path):
            search_and_unzip(f'{file_path}/')
