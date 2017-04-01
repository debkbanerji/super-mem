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

class MemeDecomposer:

    def __init__(self, img_h, img_w):
        self.DEFAULT_MASK = np.zeros((img_h+2, img_w+2), np.uint8)
        self.img_h = img_h
        self.img_w = img_w


    # via morphology
    def dilate(self, ary, N, iterations):
        """Dilate using an NxN '+' sign shape. ary is np.uint8."""
        kernel = np.zeros((N,N), dtype=np.uint8)
        kernel[(N-1)//2,:] = 1
        dilated_image = cv2.dilate(ary // 255, kernel, iterations=iterations)

        kernel = np.zeros((N,N), dtype=np.uint8)
        kernel[:,(N-1)//2] = 1
        dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
        return dilated_image

    def flood_find_regions(self, img, seed_pt, draw=False, mask=None, flood_data=(-1, -1, 0), canny_threshold_lo_hi=(-1, -1), n_dilation_iter=1):
        mask = mask or self.DEFAULT_MASK
        flood_lo, flood_hi, flood_flags = flood_data
        canny_threshold_lo, canny_threshold_hi = canny_threshold_lo_hi

        flooded = img.copy()
        mask[:] = 0
        cv2.floodFill(flooded, mask, seed_pt, (0, 255, 0), (flood_lo,)*3, (flood_hi,)*3, flood_flags)
        cv2.circle(flooded, seed_pt, 2, (0, 0, 255), -1)
        flood_region = img - flooded # todo use a better strategy here. thresholding?
        edges = cv2.Canny(flood_region, canny_threshold_lo, canny_threshold_hi, apertureSize=5)
        dilated_img = self.dilate(edges, N=3, iterations=n_dilation_iter)
        im2, contours, hierarchy = cv2.findContours(dilated_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_drawing = np.zeros((h, w, 3), np.uint8)
        cv2.drawContours(contour_drawing, contours, -1, (0,255,0), 3)
        for cnt in contours:
            x,y,r_width,r_height = cv2.boundingRect(cnt)
            cv2.rectangle(contour_drawing, (x,y),(x+r_width,y+r_height),(0,0,255),2)
        if draw:
            cv2.imshow('floodfill', flooded)
            cv2.imshow('edge', contour_drawing)

    def extract_image_regions(self, img, regions):
        
        pass

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
    seed_pt = None
    fixed_range = False
    connectivity = 4
    meme_decomposer = MemeDecomposer(h, w)

    def update(dummy=None):
        if seed_pt is None:
            cv2.imshow('floodfill', img)
            return
        lo = cv2.getTrackbarPos('lo', 'floodfill')
        hi = cv2.getTrackbarPos('hi', 'floodfill')
        thrs1 = cv2.getTrackbarPos('thrs1', 'edge')
        thrs2 = cv2.getTrackbarPos('thrs2', 'edge')
        dilation_iterations = cv2.getTrackbarPos('dilation_iterations', 'edge')
        flags = connectivity
        if fixed_range:
            flags |= cv2.FLOODFILL_FIXED_RANGE
        meme_decomposer.flood_find_regions(img, seed_pt, draw=True, flood_data=(lo,hi, flags), canny_threshold_lo_hi=(thrs1, thrs2), n_dilation_iter=dilation_iterations)



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
    cv2.createTrackbar('dilation_iterations', 'edge', 3, 10, update)

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
