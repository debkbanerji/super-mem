#!/usr/bin/env python

'''
Floodfill sample.

Usage:
  floodfill.py [<image>]

  Click on the image to set seed point

Keys:
  f     - toggle floating range
  c     - toggle 4/8 connectivity
  ESC   - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2

if __name__ == '__main__':
    import sys
    fn = sys.argv[1]
    print(__doc__)
    cv2.namedWindow('edge')

    img = cv2.imread(fn, True)
    if img is None:
        print('Failed to load image file:', fn)
        sys.exit(1)

    h, w = img.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    seed_pt = None
    fixed_range = True
    connectivity = 4

    def update(dummy=None):
        if seed_pt is None:
            cv2.imshow('floodfill', img)
            return
        flooded = img.copy()
        mask[:] = 0
        lo = cv2.getTrackbarPos('lo', 'floodfill')
        hi = cv2.getTrackbarPos('hi', 'floodfill')
        thrs1 = cv2.getTrackbarPos('thrs1', 'edge')
        thrs2 = cv2.getTrackbarPos('thrs2', 'edge')
        flags = connectivity
        if fixed_range:
            flags |= cv2.FLOODFILL_FIXED_RANGE
        cv2.floodFill(flooded, mask, seed_pt, (0, 255, 0), (lo,)*3, (hi,)*3, flags)
        cv2.circle(flooded, seed_pt, 2, (0, 0, 255), -1)
        flood_region = img - flooded
        edge = cv2.Canny(flood_region, thrs1, thrs2, apertureSize=5)
        im2, contours, hierarchy = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow('floodfill', flooded)
        buff = np.zeros((h, w), np.uint32)
        copy_flooded = image = np.zeros((h, w, 3), np.uint8)
        cv2.drawContours(copy_flooded, contours, -1, (0,255,0), 3)
        for cnt in contours:
            x,y,r_width,r_height = cv2.boundingRect(cnt)
            cv2.rectangle(copy_flooded, (x,y),(x+r_width,y+r_height),(0,0,255),2)
        cv2.imshow('edge', copy_flooded)

    def onmouse(event, x, y, flags, param):
        global seed_pt
        if flags & cv2.EVENT_FLAG_LBUTTON:
            seed_pt = x, y
            update()

    update()
    cv2.setMouseCallback('floodfill', onmouse)
    cv2.createTrackbar('lo', 'floodfill', 20, 255, update)
    cv2.createTrackbar('hi', 'floodfill', 20, 255, update)
    cv2.createTrackbar('thrs1', 'edge', 2000, 5000, update)
    cv2.createTrackbar('thrs2', 'edge', 4000, 5000, update)

    while True:
        ch = cv2.waitKey()
        if ch == 27:
            break
        if ch == ord('f'):
            fixed_range = not fixed_range
            print('using %s range' % ('floating', 'fixed')[fixed_range])
            update()
        if ch == ord('c'):
            connectivity = 12-connectivity
            print('connectivity =', connectivity)
            update()
    cv2.destroyAllWindows()
