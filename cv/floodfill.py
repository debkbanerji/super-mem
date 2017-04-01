#!/usr/bin/env python3

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
from time import sleep

# hierarchy structure:
# http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
CV_CONTOUR_PARENT = 2

def make_blank_img(h, w):
    return np.zeros((h, w, 3), np.uint8)

def get_normalized_dimensions(width, height):
    return 250, int(250/width * height)

def img_normalize_dimensions(img, width=-1, height=-1):
    new_dims = get_normalized_dimensions(width, height)
    return cv2.resize(img, new_dims), new_dims

def grab_rgb(image, rect):
    x, y, r_width, r_height = rect
    return img[y:y+r_height, x:x+r_width]

def transform_rect(rect, scale_hw):
    height_scale, width_scale = scale_hw
    x, y, r_width, r_height = rect
    x = round(x * width_scale)
    y = round(y * height_scale)
    r_width = round(r_width * width_scale)
    r_height = round(r_height * height_scale)
    return (x, y, r_width, r_height)

class MemeDecomposer:

    def __init__(self, img_raw, img_h, img_w):
        self.img_raw = img_raw
        scaled_w, scaled_h = get_normalized_dimensions(img_w, img_h)
        self.DEFAULT_MASK = np.zeros((scaled_h+2, scaled_w+2), np.uint8)
        self.img_h = img_h
        self.img_w = img_w
        self.flood_scale_factor_hw = (img_h / scaled_h, img_w / scaled_w)


    # via morphology blog post
    # http://www.danvk.org/2015/01/07/finding-blocks-of-text-in-an-image-using-python-opencv-and-numpy.html
    def dilate(self, ary, N, iterations):
        """Dilate using an NxN '+' sign shape. ary is np.uint8."""
        kernel = np.zeros((N,N), dtype=np.uint8)
        kernel[(N-1)//2,:] = 1
        dilated_image = cv2.dilate(ary // 255, kernel, iterations=iterations)

        kernel = np.zeros((N,N), dtype=np.uint8)
        kernel[:,(N-1)//2] = 1
        dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
        return dilated_image


    def flood_find_regions(self, seed_pt, draw=False, mask=None, flood_data=(-1, -1, 0), canny_threshold_lo_hi=(-1, -1), n_dilation_iter=1):
        mask = mask or self.DEFAULT_MASK
        flood_lo, flood_hi, flood_flags = flood_data
        canny_threshold_lo, canny_threshold_hi = canny_threshold_lo_hi
        working_img, scaled_dims = img_normalize_dimensions(self.img_raw.copy(), width=self.img_w, height=self.img_h)
        working_img = cv2.bilateralFilter(working_img, 11, 17, 25)
        flooded = working_img.copy()
        mask[:] = 0
        cv2.floodFill(flooded, mask, seed_pt, (0, 255, 0), (flood_lo,)*3, (flood_hi,)*3, flood_flags)
        cv2.circle(flooded, seed_pt, 2, (0, 0, 255), -1)
        flood_region = working_img - flooded # todo use a better strategy here. thresholding?
        edges = cv2.Canny(flood_region, canny_threshold_lo, canny_threshold_hi, apertureSize=5)
        dilated_img = self.dilate(edges, N=3, iterations=n_dilation_iter)
        im2, contours, hierarchy = cv2.findContours(dilated_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_drawing = make_blank_img(h, w)
        rectangle_contours = []
        leftovers = []
        for cnt, contour_meta in zip(contours, hierarchy[0]):
            epsilon = 0.1*cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,epsilon,True)
            if len(approx) == 4:
                if contour_meta[CV_CONTOUR_PARENT] != -1:
                    print('dropping contour because it is not innermost.')
                    # leftovers.append(cnt)
                else:
                    rectangle_contours.append(approx)
            else:
                leftovers.append(cnt)


        if draw:
            cv2.drawContours(contour_drawing, rectangle_contours, -1, (0,255,0), 3)
            cv2.drawContours(contour_drawing, leftovers, -1, (255,255,0), 3)
            cv2.imshow('floodfill', flooded)
            cv2.imshow('edge', contour_drawing)

        return contours, rectangle_contours, flood_region

    def extract_image_regions(self, flooded_image, rectangle_contours):
        imgs_extracted = []
        for cnt in rectangle_contours:
            normed_rect = cv2.boundingRect(cnt)
            full_rect = transform_rect(normed_rect, self.flood_scale_factor_hw)
            x, y, w, h = full_rect
            blank = make_blank_img(h, w)
            blank[:] = grab_rgb(self.img_raw, full_rect)
            imgs_extracted.append((full_rect, blank))

        print(len(imgs_extracted))
        for rect, buff in imgs_extracted:
            cv2.imshow(str(rect), buff)

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
    fixed_range = True
    connectivity = 4
    meme_decomposer = MemeDecomposer(img, h, w)

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

        contours, rect_regions, flooded_img = meme_decomposer \
            .flood_find_regions(seed_pt, draw=True,
                                flood_data=(lo, hi, flags),
                                canny_threshold_lo_hi=(thrs1, thrs2),
                                n_dilation_iter=dilation_iterations)
        meme_decomposer.extract_image_regions(flooded_img, rect_regions)




    def onmouse(event, x, y, flags, param):
        global seed_pt
        if flags & cv2.EVENT_FLAG_LBUTTON:
            seed_pt = x, y
            update()

    update()
    cv2.setMouseCallback('floodfill', onmouse)
    cv2.createTrackbar('lo', 'floodfill', 30, 255, update)
    cv2.createTrackbar('hi', 'floodfill', 50, 255, update)
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
