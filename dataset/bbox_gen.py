import cv2
import numpy as np
import argparse
import os
import json

def iswhite(p):
    return p[0] > 180 and p[1] > 180 and p[2] > 180

def convert(o):
    if isinstance(o, np.int64): 
        return int(o)  
    else:
        return o

def avgcolor(img):
    sum = [0,0,0]
    ctr = 0
    eps=0
    rows,cols, _ = img.shape
    for i in range(eps, rows - eps):
        for j in range(eps, cols - eps):
            p = img[i,j]
            if not iswhite(p):
                for c in range(3):
                    sum[c] = sum[c] + p[c]
                ctr=ctr+1

    if ctr == 0:
        return [0,0,0]
    return [sum[j]/ctr for j in range(3)]

def process_img(in_dir, out_dir, name):
    image = cv2.imread(os.path.join(in_dir, name))
    gray = 255 - cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes = {}
    for i in range(8):
        boxes[i] = []
    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for k, c in enumerate(cnts):
        x,y,w,h = cv2.boundingRect(c)
        subimg = image[y:y+h, x:x+w]
        c = avgcolor(subimg)
        hashcode = sum([(c[j] > 220) * (2**j) for j in range(3)])
        boxes[hashcode].append([x,y,x+w,y+h])
    bboxes=[]
    for k in boxes.keys():
        if not boxes[k]:
            continue
        m = 0

        perchannel = np.array(boxes[k]).transpose()
        xmin, ymin = np.min(perchannel[0]),np.min(perchannel[1])
        xmaks, ymaks = np.max(perchannel[2]),np.max(perchannel[3]) 
        bboxes.append([xmaks, ymaks, xmaks-xmin, ymaks-ymin])
        color = list(np.random.random(size=3) * 256)
        cv2.rectangle(image, (xmin, ymin), (xmaks, ymaks), color, 1)
    annotations.append({'name': name, 'op': bboxes[0], 'exprs': sorted(bboxes[1:])})

    cv2.imwrite(os.path.join(out_dir, name), image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-dir', help='input directory', required=True, type=str)
    parser.add_argument('--out-dir', help='output directory', required=True, type=str)
    parser.add_argument('--save', help='save file', required=False, type=str)

    args = parser.parse_args()
    input_names = os.listdir(args.in_dir)

    if not os.path.isfile(args.out_dir):
        os.mkdir(args.out_dir)

    annotations = []

    for name in input_names:
        process_img(args.in_dir, args.out_dir, name)
    json_output = json.dumps(annotations, default=convert)
    
    if not args.save:
        print(json_output)
    else:
        with open(args.save, 'w+') as savefile:
            savefile.write(json_output)