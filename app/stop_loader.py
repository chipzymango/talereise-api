# load all stop names in a data structure to then be used when post processing is needed
import os
import pandas as pd

def load_stop_names():
    this_dir = os.path.dirname(__file__)
    csv_path = os.path.join(this_dir, "stops.csv")

    df = pd.read_csv(csv_path, header=None)
    stop_names = df[0].dropna().unique().tolist()
    return stop_names