import argparse
import os
import json
import random
from multiprocessing import Pool
from typing import Tuple

def rescale_img(rescale_data: Tuple[str, int]):
    path, depth = rescale_data
    print(f'rescale img with {path}, {depth}')


def generate_aug(cfg: dict, dataset_path: str):
    threads = cfg['threads']
    perlvl = cfg['samples-lvl-percent']

    assert(all([v >= 0 and v <= 1 for v in perlvl.values()]))
    assert(sum(perlvl.values()) <= 1)


    imgs_names = set(os.listdir(os.path.join(dataset_path, 'output_proper')))
    to_scale = dict()
    dataset_size = len(imgs_names)
    print(dataset_size)
    for k, v in perlvl.items():
        samples = int(v * dataset_size)
        to_scale[k] = random.sample(imgs_names, samples)
        imgs_names = imgs_names.difference(set(to_scale[k]))

    print(to_scale)

    with Pool(processes=threads) as pool:
        pool.map(rescale_img, [(v, int(k)) for k, v in to_scale.items()])

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--aug-job', help='Augmentation job config file path', required=True, type=str)
    parser.add_argument(
        '--dataset', help='Path to dataset', required=True, type=str)

    """ AUG-JOB
        "samples-lvl-percent": {
        "0": any - any value doesn't matter there - 0 means that it has 0 depth
        "1": 0.1, <-- 10% from dataset will be rescaled as it is 1-depth node
        .
        .
        .
        "N": 0.1
    }
    """

    args = parser.parse_args()
    config_path = args.aug_job
    dataset_path = args.dataset
    with open(config_path, 'r') as cfg_file:
        cfg = json.loads(cfg_file.read())

    generate_aug(cfg, dataset_path)
