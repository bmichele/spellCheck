import time
import logging
import requests
import os
import os.path as path
import zipfile


def download_embeddings(folder: str, model_name: str) -> None:
    '''
    Function to download fasttext embeddings from https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/
    Before downloading, it checks if the model files are already present in the specified folder.
    '''
    logging.info('Looking for fasttext embeddings in folder {}'.format(path.abspath(folder)))
    if (model_name + '.bin' not in os.listdir(folder)) or (model_name + '.bin' not in os.listdir(folder)):
        if model_name + '.zip' not in os.listdir(folder):
            url = 'https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/{}.zip'.format(model_name)
            logging.info('Downloading {} from {}'.format(model_name, url))
            t0 = time.time()
            r = requests.get(url)
            with open(path.join(folder, model_name + '.zip')) as f:
                f.write(r.content)
            logging.info('Downloaded file in {} seconds'.format(time.time() - t0))
        logging.info('Inflating {} in folder {}'.format(model_name + '.zip', folder))
        with zipfile.ZipFile(path.join(folder, model_name + '.zip'), 'r') as zip_ref:
            zip_ref.extractall()
