import argparse
import json
import cv2
from pathlib import Path


def crop_img(img, bbox):
    x, y, w, h = bbox
    return img[y:y + h, x:x + w]


def process_img_from_annots(img_path, img_bbox):
    img = cv2.imread(str(img_path))
    return crop_img(img, img_bbox)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-black-dir', help='output_black dir path (input)',
                        required=True, type=str)
    parser.add_argument('--out-op-dir', help='output_ops dir path (output)',
                        required=True, type=str)
    parser.add_argument('--annotations-json', help='annotations.json path',
                        required=True, type=str)

    args = parser.parse_args()
    out_black_path = Path(args.out_black_dir)
    out_ops_path = Path(args.out_op_dir)
    if not out_ops_path.is_dir():
        out_ops_path.mkdir()

    with open(args.annotations_json, 'r') as annots_file:
        annots = json.load(annots_file)

    processed_imgs = [
        (process_img_from_annots(out_black_path / annot['name'], annot['op']),
         annot['name']) for
        annot in annots]

    for img, name in processed_imgs:
        cv2.imwrite(str(out_ops_path / name), img)
