import subprocess
from subprocess import CalledProcessError
import argparse
import os
import numpy as np
import json
from uuid import uuid4


def generate_aug(cfg: dict, dataset_path: str):
    threads = cfg['threads']
    perlvl = cfg['samples-lvl-percent']

    assert(all([v >= 0 and v <= 1 for v in perlvl.values()]))
    assert(sum(perlvl.values()) <= 1)

    imgs_names = os.listdir(os.path.join(dataset_path, 'output_paper'))


    

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
