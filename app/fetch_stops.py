import xml.etree.ElementTree as ET
import os
from utils import download_and_extract

def fetch_stop_names(save_path):

    download_and_extract("https://storage.googleapis.com/marduk-production/tiamat/03_Oslo_latest.zip", save_path)
    download_and_extract("https://storage.googleapis.com/marduk-production/tiamat/32_Akershus_latest.zip", save_path)

    stop_places = set()

    namespaces = {
        'netex': "http://www.netex.org.uk/netex",
        'gml': "http://www.opengis.net/gml/3.2"
    }
    print("Extracting stop places...")

    if len(os.listdir(save_path)) <= 0:
        print(f"Could not find any stop places in: '{save_path}'")
    else:
        for file in os.listdir(save_path):
            file = os.path.join(save_path, file)
            tree = ET.parse(file)
            root = tree.getroot()
            for stop_place in root.findall('.//netex:StopPlace', namespaces):
                name = stop_place.find('netex:Name', namespaces).text
                stop_places.add(name)

        return stop_places