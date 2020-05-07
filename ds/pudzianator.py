import cv2
import numpy as np

def iswhite(p):
    return p[0] > 180 and p[1] > 180 and p[2] > 180

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

image = cv2.imread('sample2.png')
oriimg = image.copy()
gray = 255 - cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

boxes = {}

for i in range(8):
    boxes[i] = []
cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for k, c in enumerate(cnts):
    x,y,w,h = cv2.boundingRect(c)
    cv2.imwrite('tst.png', oriimg)
    subimg = oriimg[y:y+h, x:x+w]
    #cv2.imwrite(f'image{k}.png', subimg)
    c = avgcolor(subimg)
    hashcode = sum([(c[j] > 220) * (2**j) for j in range(3)])
    boxes[hashcode].append([x,y,x+w,y+h])
    #print(k, c)
    #color = list(np.random.random(size=3) * 256)
    #cv2.rectangle(image, (x, y), (x + w, y + h), color, 4)
print(boxes)
for k in boxes.keys():
    if not boxes[k]:
        continue
    m = 0
    print('xxx')
    print(boxes[k])
    print(np.array(boxes[k]).transpose())
    #exit(0)

    perchannel = np.array(boxes[k]).transpose()
    xmin, ymin = np.min(perchannel[0]),np.min(perchannel[1])
    xmaks, ymaks = np.max(perchannel[2]),np.max(perchannel[3]) 
    print(xmin,ymin,xmaks,ymaks)
    color = list(np.random.random(size=3) * 256)
    cv2.rectangle(oriimg, (xmin, ymin), (xmaks, ymaks), color, 1)

cv2.imshow('image', image)
cv2.imwrite('image.png', image)
cv2.imwrite('oriimg.png', oriimg)

#cv2.waitKey()