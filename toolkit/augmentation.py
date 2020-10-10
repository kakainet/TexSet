import cv2
import argparse
import os
import numpy as np
import json


def generate_aug(cfg: dict):
    multithread = cfg['parts']
    perlvl = cfg['samples-in-part-per-lvl']

    for idx, lvl in enumerate(perlvl):
        print(f'Level {idx}: {lvl} samples')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--job', help='Augmentation job config file path', required=True, type=str)

    args = parser.parse_args()
    config_path = args.job

    with open(config_path, 'r') as cfg_file:
        cfg = json.loads(cfg_file.read())

    generate_aug(cfg)
