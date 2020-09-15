from preprocessing import concatenate_and_generate_overview
from preprocessing import unzipify

data_path = "data"
unzipped = True

if __name__ == '__main__':
    if not unzipped:
        unzipify.search_and_unzip(data_path)
    print("done unzipify")
    concatenate_and_generate_overview.search_and_concat(data_path)
