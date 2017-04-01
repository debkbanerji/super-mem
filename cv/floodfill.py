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
import os

# hierarchy structure:
# http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
CV_CONTOUR_PARENT = 2
IMAGE_NORM_WIDTH = 500
IMAGE_OCR_MIN_DIM = 25
IMAGE_SUBCOMPONENT_THRESHOLD = 30 * 30 # if less than some value of pixels (in the normed img), throw it out
COLOR_BLACK = (0,0,0)
COLOR_GREEN = (0,255,0)

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def make_blank_img(h, w):
    return np.zeros((h, w, 3), np.uint8)

def get_normalized_dimensions(width, height):
    return IMAGE_NORM_WIDTH, int(IMAGE_NORM_WIDTH/width * height)

def img_normalize_dimensions(img, width=-1, height=-1):
    new_dims = get_normalized_dimensions(width, height)
    return cv2.resize(img, new_dims), new_dims

# based on http://stackoverflow.com/a/26445324
def grab_rgb(image, rect):
    x, y, r_width, r_height = rect
    return image[y:y+r_height, x:x+r_width]

def put_fill_rect(mask, rect, fill):
    x, y, r_width, r_height = rect
    cv2.rectangle(mask, (x, y), (x+r_width,y+r_height), fill, -1)

def transform_rect(rect, scale_hw):
    height_scale, width_scale = scale_hw
    x, y, r_width, r_height = rect
    x = round(x * width_scale)
    y = round(y * height_scale)
    r_width = round(r_width * width_scale)
    r_height = round(r_height * height_scale)
    return (x, y, r_width, r_height)

def contours_to_rectangles(contour_rects):
    for cnt in contour_rects:
        yield cv2.boundingRect(cnt), cnt

# via morphology blog post
# http://www.danvk.org/2015/01/07/finding-blocks-of-text-in-an-image-using-python-opencv-and-numpy.html
def dilate(ary, N, iterations, method=cv2.dilate):
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[(N-1)//2,:] = 1
    dilated_image = method(ary // 255, kernel, iterations=iterations)

    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[:,(N-1)//2] = 1
    dilated_image = method(dilated_image, kernel, iterations=iterations)
    return dilated_image

class MemeDecomposer:
    def __init__(self, img_raw, img_h, img_w):
        self.img_raw = img_raw
        scaled_w, scaled_h = get_normalized_dimensions(img_w, img_h)
        self.DEFAULT_MASK = np.zeros((scaled_h+2, scaled_w+2), np.uint8)
        self.img_h = img_h
        self.img_w = img_w
        self.flood_scale_factor_hw = (img_h / scaled_h, img_w / scaled_w)


    def get_working_image(self):
        working_img, scaled_dims = img_normalize_dimensions(self.img_raw.copy(), width=self.img_w, height=self.img_h)
        return working_img, scaled_dims

    def flood_find_regions(self, seed_pt, draw=False, mask=None, flood_data=(-1, -1, 0), canny_threshold_lo_hi=(-1, -1), n_dilation_iter=1):
        mask = mask or self.DEFAULT_MASK
        working_img, scaled_dims = self.get_working_image()
        working_img = cv2.bilateralFilter(working_img, 11, 17, 25)
        flood_lo, flood_hi, flood_flags = flood_data
        canny_threshold_lo, canny_threshold_hi = canny_threshold_lo_hi
        flooded = working_img.copy()
        mask[:] = 0
        cv2.floodFill(flooded, mask, seed_pt, (0, 255, 0), (flood_lo,)*3, (flood_hi,)*3, flood_flags)
        cv2.circle(flooded, seed_pt, 2, (0, 0, 255), -1)
        flood_region = working_img - flooded # todo use a better strategy here. thresholding?
        edges = cv2.Canny(flood_region, canny_threshold_lo, canny_threshold_hi, apertureSize=5)
        dilated_img = dilate(edges, N=3, iterations=n_dilation_iter)
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
                else:
                    _, _, normed_w, normed_h = cv2.boundingRect(approx)
                    if normed_w * normed_h < IMAGE_SUBCOMPONENT_THRESHOLD:
                        print("skipping contour with dimensions %s x %s" % (normed_w, normed_h))
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
        ignored_regions = []
        for normed_rect, cnt in contours_to_rectangles(rectangle_contours):
            full_rect = transform_rect(normed_rect, self.flood_scale_factor_hw)
            x, y, w, h = full_rect
            blank = make_blank_img(h, w)
            blank[:] = grab_rgb(self.img_raw, full_rect)
            imgs_extracted.append((blank, full_rect))

        return imgs_extracted, ignored_regions

    def find_text(self, rect_regions):
        image, scaled_dims = self.get_working_image()
        image = cv2.GaussianBlur(image, (13,13), 0)
        mask = np.ones(image.shape[:2], dtype="uint8") * 255
        for rect_region, cnt in contours_to_rectangles(rect_regions): put_fill_rect(mask, rect_region, COLOR_BLACK)
        mask = dilate(mask, 3, 3, method=cv2.erode)
        edges = cv2.Canny(image, 30, 50, apertureSize=5)
        mask = cv2.bitwise_and(edges, edges, mask=mask)
        mask = dilate(mask, 3, 3)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x,y,r_width,r_height = cv2.boundingRect(cnt)
            if min(r_width, r_height) >= IMAGE_OCR_MIN_DIM:
                cv2.rectangle(image, (x, y), (x+r_width,y+r_height), COLOR_GREEN, 1)
            else:
                print("skipping potential text region with dimensions %s x %s" % (r_width, r_height))


        # cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
        cv2.imshow('edge', image)

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

        non_rect_contours, rect_regions, flooded_img = meme_decomposer \
            .flood_find_regions(seed_pt, draw=False,
                                flood_data=(lo, hi, flags),
                                canny_threshold_lo_hi=(thrs1, thrs2),
                                n_dilation_iter=dilation_iterations)
        imgs, ignored = meme_decomposer.extract_image_regions(flooded_img, rect_regions)
        meme_decomposer.find_text(rect_regions)
        cv2.drawContours(flooded_img, ignored, -1, (0,0,250), 3)
        # cv2.imshow('edge', flooded_img)

        seq = iter(range(len(imgs)))
        for img_data, pose in imgs:
            # TODO right now it's setting each image as 0.webp, 1.webp and so on. These should be uploaded to firebase
            ensure_dir('generated_img_components/')
            # cv2.imwrite('generated_img_components/' + str(next(seq)) + '.webp', img_data, [cv2.IMWRITE_WEBP_QUALITY, 20])

            # TODO write the pose data to json
            x, y, w, h = pose





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
