import argparse
import os
import json
import random
from multiprocessing import Pool
from typing import Tuple
import cv2
import itertools


def rescale_img(rescale_data: Tuple[int, str]):
    depth, path = rescale_data
    dst_path = os.path.join(dataset_path, 'output_proper', path)
    img = cv2.imread(dst_path)
    shape = list(img.shape)
    ori_shape = tuple(shape[:2])
    shape[0] = int(shape[0]*rescale_depth[depth])
    shape[1] = int(shape[1]*rescale_depth[depth])
    shape = tuple(shape[:2])
    img = cv2.resize(img, shape)
    img = cv2.resize(img, ori_shape)
    os.remove(dst_path)
    cv2.imwrite(dst_path, img)


def generate_aug(cfg: dict, dataset_path: str):
    threads = cfg['threads']
    perlvl = cfg['samples-lvl-percent']
    perlvl = {
        int(k): v for k, v in perlvl.items()
    }
    assert(all([v >= 0 and v <= 1 for v in perlvl.values()]))
    assert(sum(perlvl.values()) <= 1)

    imgs_path = os.path.join(dataset_path, 'output_proper')
    available_depths = set(entry['depth'] for entry in annots)
    max_depth = max(available_depths)
    img_names = {
        k: set(x['name'] for x in filter(lambda entry: entry['depth'] == k, annots)) for k in available_depths
    }

    to_scale = dict()
    dataset_size = {k: len(img_names[k]) for k in img_names.keys()}
    for k, v in perlvl.items():
        samples = int(v * dataset_size[k])
        to_scale[k] = random.sample(img_names[max_depth-k], samples)
        img_names[max_depth-k] = img_names[max_depth -
                                           k].difference(set(to_scale[k]))

    to_scale = list(itertools.chain.from_iterable(((int(index), path)
                                                   for path in paths) for index, paths in to_scale.items()))

    with Pool(processes=threads) as pool:
        pool.map(rescale_img, to_scale)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--aug-job', help='Augmentation job config file path', required=True, type=str)
    parser.add_argument(
        '--dataset', help='Path to dataset', required=True, type=str)
    parser.add_argument(
        '--annots-path', help='Path to annotations', required=True, type=str)
    parser.add_argument(
        '--rescale-config', help='Path to rescaling config', required=True, type=str)

    """ AUG-JOB
        "samples-lvl-percent": {
        "1": any - any value doesn't matter there - 1 means that it has 1 depth (i.e. 0)
        "2": 0.1, <-- 10% from dataset will be rescaled as it is 2-depth node
        .
        .
        .
        "N": 0.1
    }
    """

    args = parser.parse_args()
    config_path = args.aug_job
    rescale_path = args.rescale_config
    dataset_path = args.dataset
    annots_path = args.annots_path

    with open(config_path, 'r') as cfg_file:
        cfg = json.loads(cfg_file.read())

    with open(annots_path, 'r') as afile:
        annots = json.loads(afile.read())

    with open(rescale_path, 'r') as cfg_file:
        rescale_depth = json.loads(cfg_file.read())

    rescale_depth = {int(k): v for k, v in rescale_depth.items()}
    generate_aug(cfg, dataset_path)
