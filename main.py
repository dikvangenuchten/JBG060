from preprocessing import concatenate_and_generate_overview
from model import lstm
from preprocessing import unzipify
import argparse

data_path = "data"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unzipped', action='store_true', default=False, help='whether we want to do an unzipify')
    parser.add_argument('-c', '--concat', action='store_true', default=False, help='whether we want to do the concat')
    parser.add_argument('-m', '--model', action='store_true', default=False, help='whether we want to run the model')
    args = parser.parse_args()

    if args.unzipped:
        unzipify.search_and_unzip(data_path)
    if args.concat:
        concatenate_and_generate_overview.search_and_concat(data_path)
    if args.model:
        lstm.create_model()


