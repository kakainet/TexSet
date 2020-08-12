import cv2
import argparse
import os

def transform_dataset(input, output, dim):
    
    for img_entry in os.scandir(input):
        if not os.path.isfile(img_entry.path):
            continue
        img = cv2.imread(img_entry.path, cv2.IMREAD_COLOR)
        height, width, channels = img.shape
        assert(channels == 3)
        max_dim = max(height, width)
        ratio = dim/max_dim
        

    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', help='directory with dataset', required=True, type=str)
    parser.add_argument('--output-dir', help='directory where output should be exported', required=True, type=str)
    parser.add_argument('--dim', help='X/Y dim of output images', required=True, type=int)

    FLAGS = parser.parse_args()

    transform_dataset(FLAGS.input_dir, FLAGS.output_dir, FLAGS.dim)
