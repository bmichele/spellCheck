import urllib.request
from tqdm import tqdm
import logging
import time
import zipfile
import os
import os.path as path


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


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
            download_url(url, model_name + '.zip')
            logging.info('Downloaded file in {} seconds'.format(time.time() - t0))
        logging.info('Inflating {} in folder {}'.format(model_name + '.zip', folder))
        with zipfile.ZipFile(path.join(folder, model_name + '.zip'), 'r') as zip_ref:
            zip_ref.extractall()
