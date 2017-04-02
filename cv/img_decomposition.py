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

import numpy as np
import cv2
import os

# hierarchy structure:
# http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
CV_CONTOUR_PARENT = 2
IMAGE_NORM_WIDTH = 500
IMAGE_OCR_MIN_DIM = 25
IMAGE_SUBCOMPONENT_THRESHOLD = 40 * 30 # if less than some value of pixels (in the normed img), throw it out
COLOR_BLACK = (0,0,0)
COLOR_GREEN = (0,255,0)
COLOR_RED = (0,0,255)
TYPE_IMG = 0
TYPE_TEXT = 1
FLOOD_BORDER_PX=2 # dont make this higher than 2 :P TODO understand why and fix

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
def grab_rgb(image, rect, img_w, img_h):
    x, y, r_width, r_height = rect
    if y+r_height >= img_h:
        r_height = img_h - 1 -y
    if x+r_width >= img_w:
        r_width= img_w- 1 - x
    return image[y:y+r_height, x:x+r_width]

def put_fill_rect(mask, rect, fill):
    x, y, r_width, r_height = rect
    cv2.rectangle(mask, (x, y), (x+r_width,y+r_height), fill, -1)

def transform_point(point, scale_hw, offset=0):
    height_scale, width_scale = scale_hw
    x, y = point
    x+=offset
    y+=offset
    return (round(x * width_scale), round(y * height_scale))

def transform_rect(rect, scale_hw, offset=0):
    x, y, r_width, r_height = rect
    x, y = transform_point( (x,y), scale_hw, offset=offset)
    r_width, r_height = transform_point( (r_width, r_height), scale_hw, offset=offset)
    return (x, y, r_width, r_height)

def contours_to_rectangles(contour_rects):
    for cnt in contour_rects:
        yield cv2.boundingRect(cnt), cnt

# via morphology blog post
# http://www.danvk.org/2015/01/07/finding-blocks-of-text-in-an-image-using-python-opencv-and-numpy.html
# idk why they use this kernel but it works very well :)
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
        scaled_reverse = (1/self.flood_scale_factor_hw[0], 1/self.flood_scale_factor_hw[1])
        seed_pt = transform_point(seed_pt, scaled_reverse)

        working_img, scaled_dims = self.get_working_image()
        w, h = scaled_dims
        working_img = cv2.bilateralFilter(working_img, 11, 17, 25)
        flood_lo, flood_hi, flood_flags = flood_data
        canny_threshold_lo, canny_threshold_hi = canny_threshold_lo_hi
        flooded = working_img.copy()
        mask[:] = 0
        cv2.floodFill(flooded, mask, seed_pt, (0, 255, 0), (flood_lo,)*3, (flood_hi,)*3, flood_flags)
        # cv2.circle(flooded, seed_pt, 2, (0, 0, 255), -1)
        # flood_region = cv2.inRange(working_img - flooded, (0, 0, 1), (255, 255, 255))
        flood_region = cv2.cvtColor(working_img - flooded, cv2.COLOR_BGR2GRAY)
        _, flood_region = cv2.threshold(flood_region, 2, 255, cv2.THRESH_BINARY)
        flood_region = cv2.copyMakeBorder(flood_region, FLOOD_BORDER_PX, FLOOD_BORDER_PX, FLOOD_BORDER_PX, FLOOD_BORDER_PX, 0, value=(255,255,255))
        edges = cv2.Canny(flood_region, canny_threshold_lo, canny_threshold_hi, apertureSize=5)
        dilated_img = dilate(edges, 3, n_dilation_iter)
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
            cv2.imshow('main_window', flooded)
            cv2.imshow('edge', contour_drawing)

        return contours, rectangle_contours, flood_region

    def extract_image_regions(self, rectangle_contours):
        imgs_extracted = []
        ignored_regions = []
        for normed_rect, cnt in contours_to_rectangles(rectangle_contours):
            full_rect = transform_rect(normed_rect, self.flood_scale_factor_hw, offset=0)
            x, y, w, h = full_rect
            blank = make_blank_img(h, w)
            blank[:] = grab_rgb(self.img_raw, full_rect, self.img_w, self.img_h)
            print('full rect: ', full_rect)
            imgs_extracted.append((blank, full_rect))

        return imgs_extracted, ignored_regions

    def find_text(self, rect_regions, draw_graphics=False):
        image, scaled_dims = self.get_working_image()
        image = cv2.GaussianBlur(image, (9,13), 0)
        mask = np.ones(image.shape[:2], dtype="uint8") * 255
        for rect_region, cnt in contours_to_rectangles(rect_regions): put_fill_rect(mask, rect_region, COLOR_BLACK)
        mask = dilate(mask, 5, 3, method=cv2.erode)
        edges = cv2.Canny(image, 30, 50, apertureSize=5)
        mask = cv2.bitwise_and(edges, edges, mask=mask)

        if draw_graphics:
            cv2.imshow('masked_text_edges', mask)

        chars_leftright_kernel = np.zeros((3,3), dtype=np.uint8)
        chars_leftright_kernel[(3-1)//2,:] = 1 # only middle row is in kernel
        mask = cv2.dilate(mask, chars_leftright_kernel, iterations=1)
        mask = dilate(mask, 3, 2)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        old_n_contours = len(contours)
        contours = list(filter(lambda cnt: cv2.contourArea(cnt) >= 100, contours))
        print('filtered out %s contours' % (old_n_contours - len(contours)))

        resultant_text_regions = []
        for cnt in contours:
            bounding_rect = cv2.boundingRect(cnt)
            x,y,r_width,r_height = bounding_rect
            if r_height >= 6 and not r_height / r_width > 3:
                resultant_text_regions.append(cnt)
                cv2.rectangle(image, (x, y), (x+r_width,y+r_height), COLOR_GREEN, 1)
            else:
                print("skipping potential text region with dimensions %s x %s" % (r_width, r_height))
                cv2.rectangle(image, (x, y), (x+r_width,y+r_height), COLOR_RED, 1)

        if draw_graphics:
            blank = make_blank_img(self.img_h, self.img_w)
            blank= cv2.drawContours(blank, contours, -1, (0, 255, 0), 3)
            cv2.imshow('edge', blank)
            cv2.imshow('main_window', image)

        return resultant_text_regions

def decompose_image(img_filepath, dest_folder, draw_graphics=False):
    img = cv2.imread(img_filepath, True)
    if img is None:
        raise "Failed to load the file at %s" % img_filepath

    h, w = img.shape[:2]
    seed_pt = (w - 5, 5) # super advanced hackathon grade seeding algorithm
    fixed_range = True
    connectivity = 4
    meme_decomposer = MemeDecomposer(img, h, w)
    lo = 30
    hi = 50
    thrs1 = 2000
    thrs2 = 4000
    dilation_iterations = 3

    flags = connectivity | cv2.FLOODFILL_FIXED_RANGE

    non_rect_contours, rect_regions, flooded_img = meme_decomposer \
        .flood_find_regions(seed_pt, draw=draw_graphics,
                            flood_data=(lo, hi, flags),
                            canny_threshold_lo_hi=(thrs1, thrs2),
                            n_dilation_iter=dilation_iterations)
    imgs, ignored = meme_decomposer.extract_image_regions(rect_regions)
    text_regions = meme_decomposer.find_text(rect_regions)
    text_imgs, _ = meme_decomposer.extract_image_regions(text_regions)

    decomp_objects = []

    i = 0
    for img_data, pose in imgs:
        uri = '%s/asset_%s.webp' % (dest_folder, i)
        cv2.imwrite(uri, img_data, [cv2.IMWRITE_WEBP_QUALITY, 100])
        decomp_objects.append(DecompObject(uri, TYPE_IMG, pose))
        i += 1

    for tr, pose in text_imgs:
        uri = '%s/ocr_%s.png' % (dest_folder, i)
        cv2.imwrite(uri, tr)
        decomp_objects.append(DecompObject(uri, TYPE_TEXT, pose))
        i += 1

    return decomp_objects

class DecompObject():
    def __init__(self, file_path, type, pose):
        self.file_path = file_path
        self.type = type
        self.pose = pose

    def type(self):
        return self.type;

    def file_path(self):
        return self.file_path

    def pose(self):
        return self.pose

    def __dict__(self):
        x,y,w,h = self.pose
        return {
            'x': x,
            'y': y,
            'width': w,
            'height': h
        }

    def __repr__(self):
        return "%s, %s, %s" % (self.file_path, self.type, self.pose)

if __name__ == '__main__':
    import sys
    img_path = sys.argv[1]
    print(__doc__)
    cv2.namedWindow('edge')
    decompose_image(img_path, '.', draw_graphics=True)

    while cv2.waitKey(0) != 97: pass
    cv2.destroyAllWindows()


