import xml.etree.ElementTree as ET
import requests
import zipfile
import os

def download_and_extract(url, save_path, keep_zip=False):
    save_path = save_path + ".zip"
    print("Downloading from: " + url)
    r = requests.get(url, stream=True)

    # download zip file with the given download name
    with open(save_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    # extract zip file
    zip_extract_folder = save_path.replace(".zip", "")
    print("Extracting to: " + zip_extract_folder)
    with zipfile.ZipFile(save_path, "r") as zip_ref:
        zip_ref.extractall(zip_extract_folder)
        zip_ref.close()

    if not keep_zip:
        print("Deleting remaining zip files...")
        os.remove(save_path)