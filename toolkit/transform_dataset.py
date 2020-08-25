import cv2
import argparse
import os
import numpy as np
import json


def sort_annotations(jsonsource):
    def compare(entry):
        def get_idx(entry): return int(
            entry['name'][len('eq'):entry['name'].find('.')])
        return get_idx(entry)

    return sorted(jsonsource, key=compare)


def update_by_ratio(annotjson, idx, ratio):
    annotjson[idx]['op'] = [int(x * ratio) for x in annotjson[idx]['op']]
    annotjson[idx]['exprs'] = [[int(x * ratio) for x in coords]
                               for coords in annotjson[idx]['exprs']]


def update_by_shift(annotjson, idx, shift, vertical):
    if vertical:
        annotjson[idx]['op'] = [int(x + shift * (i % 2 == 1 and i < 2))
                                for i, x in enumerate(annotjson[idx]['op'])]
        annotjson[idx]['exprs'] = [[(x + shift * (i % 2 == 1 and i < 2))
                                    for i, x in enumerate(coords)] for coords in annotjson[idx]['exprs']]
    else:
        annotjson[idx]['op'] = [int(x + shift * (i % 2 == 0 and i < 2))
                                for i, x in enumerate(annotjson[idx]['op'])]
        annotjson[idx]['exprs'] = [[int(x + shift * (i % 2 == 0 and i < 2))
                                    for i, x in enumerate(coords)] for coords in annotjson[idx]['exprs']]


def transform_dataset(input, output, dim):
    idx = 0
    for img_entry in os.scandir(input):
        if not os.path.isfile(img_entry.path):
            continue
        img = cv2.imread(img_entry.path, cv2.IMREAD_COLOR)
        height, width, channels = img.shape
        assert(channels == 3)
        max_dim = max(height, width)
        ratio = dim/max_dim
        dsize = (round(width*ratio), round(height*ratio))
        update_by_ratio(annotjson, idx, ratio)
        img = cv2.resize(img, dsize)
        assert(dim in img.shape)
        h, w, _ = img.shape
        delta = abs(w-h)
        shift = round(delta/2)
        if h > w:
            strip = 255 * np.ones(shape=[dim, shift, channels], dtype=np.uint8)
            img = np.hstack([img, strip])
            img = np.hstack([strip, img])
            update_by_shift(annotjson, idx, shift, False)
        elif w > h:
            strip = 255 * np.ones(shape=[shift, dim, channels], dtype=np.uint8)
            img = np.vstack([img, strip])
            img = np.vstack([strip, img])
            update_by_shift(annotjson, idx, shift, True)

        cv2.imwrite(os.path.join(output, img_entry.name),
                    cv2.resize(img, (dim, dim)))
        idx += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-dir', help='directory with dataset', required=True, type=str)
    parser.add_argument(
        '--output-dir', help='directory where output should be exported', required=True, type=str)
    parser.add_argument(
        '--dim', help='X/Y dim of output images', required=True, type=int)
    parser.add_argument(
        '--annotations', help='annotations file', required=True, type=str)

    FLAGS = parser.parse_args()
    annotations = FLAGS.annotations
    annotpath, annotfilename = os.path.split(os.path.abspath(annotations))

    with open(annotations, 'r') as annotfile:
        annotjson = json.loads(annotfile.read())

    annotjson = sort_annotations(annotjson)

    if not os.path.isdir(FLAGS.output_dir):
        os.mkdir(FLAGS.output_dir)

    transform_dataset(FLAGS.input_dir, FLAGS.output_dir, FLAGS.dim)

    with open(os.path.join(annotpath, annotfilename), 'w+') as output:
        output.write(json.dumps(annotjson))
