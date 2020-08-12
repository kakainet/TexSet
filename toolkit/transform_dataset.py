import cv2
import argparse
import os
import numpy as np

def transform_dataset(input, output, dim):
    for img_entry in os.scandir(input):
        if not os.path.isfile(img_entry.path):
            continue
        img = cv2.imread(img_entry.path, cv2.IMREAD_COLOR)
        height, width, channels = img.shape
        assert(channels == 3)
        max_dim = max(height, width)
        ratio = dim/max_dim
        dsize = (round(width*ratio), round(height*ratio))
        img = cv2.resize(img, dsize)
        #whiteimg = 255 * np.ones(shape=[dim, dim, channels], dtype=np.uint8)
        assert(dim in img.shape)
        h, w, _ = img.shape
        delta = abs(w-h)
        shift = round(delta/2)
        if h > w:
            strip = 255 * np.ones(shape=[dim, shift, channels], dtype=np.uint8)
            img = np.hstack([img, strip])
            img = np.hstack([strip, img])
        elif w > h:
            strip = 255 * np.ones(shape=[shift, dim, channels], dtype=np.uint8)
            img = np.vstack([img, strip])
            img = np.vstack([strip, img])

        cv2.imwrite(os.path.join(output, img_entry.name), cv2.resize(img, (dim, dim)))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', help='directory with dataset', required=True, type=str)
    parser.add_argument('--output-dir', help='directory where output should be exported', required=True, type=str)
    parser.add_argument('--dim', help='X/Y dim of output images', required=True, type=int)

    FLAGS = parser.parse_args()

    if not os.path.isdir(FLAGS.output_dir):
        os.mkdir(FLAGS.output_dir)

    transform_dataset(FLAGS.input_dir, FLAGS.output_dir, FLAGS.dim)
