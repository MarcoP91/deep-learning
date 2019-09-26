import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import imutils
import math
import glob
from scipy import ndimage


def show_wait_destroy_3d(winname, img):
    rows,cols = img.shape[:2]
    imS = cv.resize(img, (rows//4, cols//4))
    #imS = img
    cv.imshow(winname, imS)   
    cv.moveWindow(winname, 300, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)
    cv.waitKey(1)
    

def show_wait_destroy_particular(winname, img):

    cv.imshow(winname, img)   
    cv.moveWindow(winname, 300, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)
    cv.waitKey(1)
    

def show_wait_destroy(winname, img):
    rows,cols = img.shape
    imS = cv.resize(img, (rows//4, cols//4))
    #imS = img
    cv.imshow(winname, imS)   
    cv.moveWindow(winname, 300, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)
    cv.waitKey(1)
    

def extract_lines(src):
    # [gray]
    # Transform source image to gray if it is not already
    if len(src.shape) != 2:
        gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    else:
        gray = src

    gray = cv.bitwise_not(gray)
    bw = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, \
                                cv.THRESH_BINARY, 15, -2)

    horizontal = np.copy(bw)
    vertical = np.copy(bw)

    cols = horizontal.shape[1]
    horizontal_size = cols // 30
    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv.getStructuringElement(cv.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv.erode(horizontal, horizontalStructure)
    #show_wait_destroy_particular("horizontal", horizontal)
    horizontal = cv.dilate(horizontal, horizontalStructure, iterations=6)
    
    # [vert]
    # Specify size on vertical axis
    rows = vertical.shape[0]
    verticalsize = rows // 30
    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv.getStructuringElement(cv.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    vertical = cv.erode(vertical, verticalStructure)
    #show_wait_destroy_particular("vertical", vertical)
    vertical = cv.dilate(vertical, verticalStructure, iterations=6)

    
    result = cv.addWeighted(vertical,1,horizontal,1,0)

    #show_wait_destroy_particular('result', result)

    res2 = cv.add(result, src);
    #show_wait_destroy_particular('result2', res2)
    return res2


def find_best_angle(img_before):
 
    img_gray = img_before
    img_edges = cv.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=800, maxLineGap=30)

    angles = []

    for x1, y1, x2, y2 in lines[0]:
        cv.line(img_before, (x1, y1), (x2, y2), 0, 1)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    img_rotated = ndimage.rotate(img_before, median_angle)
    #show_wait_destroy("After", img_rotated) 
    print("Angle is {}".format(median_angle))
    return img_rotated


def find_bounding_boxes_fixed(img, maxLoc, w, h,scaled=0, ratio = 1):
    global COUNTER
    top_left = maxLoc
    
    license_hieight = int(h * 1.2 * ratio) + scaled
    license_width = int(w * 5.2 * ratio) + scaled
    top_left_license_w = int(top_left[0]  - (w *2.4*ratio)) - scaled//2
    if top_left_license_w < 0:
        top_left_license_w = 0
    top_left_license_h = int(top_left[1] + (h * 4.7*ratio)) - scaled//2
    if top_left_license_h < 0:
        top_left_license_h = 0
        
    top_left_license = (top_left_license_w, top_left_license_h)
    bottom_right_license = (top_left_license[0] + license_width, top_left_license[1] + license_hieight)

    date_hieight = int(h * 1.5 * ratio) + scaled
    date_width = int(w * 3.5 * ratio) + scaled
    
    top_left_date = (int(top_left[0]  + (w *4* ratio)), int(top_left[1] - (h * 2.4 * ratio)) - scaled//2)
    bottom_right_date = (top_left_date[0] + date_width, top_left_date[1] + date_hieight)

    vin_hieight = int(h * 1.3 * ratio) + scaled
    vin_width = int(w * 5.5 * ratio) + scaled
    
    top_left_vin = (top_left_date[0] , int(top_left[1] - (h * 1 * ratio)) - scaled//2)
    bottom_right_vin = (top_left_vin[0] + vin_width, top_left_vin[1] + vin_hieight)      
        
    sub_img_lic = img[top_left_license[1]:bottom_right_license[1], top_left_license[0]:bottom_right_license[0]]

    
#     try:
#         show_wait_destroy_particular('license',sub_img_lic)

#     except:
#         print('License outside of bounds')
     
    sub_img_date = img[top_left_date[1]:bottom_right_date[1], top_left_date[0]:bottom_right_date[0]]

#     try:
#         show_wait_destroy_particular('date',sub_img_date)

#     except:
#         print('Date outside of bounds')
     
    sub_img_vin = img[top_left_vin[1]:bottom_right_vin[1], top_left_vin[0]:bottom_right_vin[0]]


#     try:
#         show_wait_destroy_particular('vin',sub_img_vin)

#     except:
#         print('Vin outside of bounds')
    
    return sub_img_lic, sub_img_date, sub_img_vin


def find_logo_scale_rotation(img):
    template_hl = cv.imread('./../logos/logo_hl.png',0)
    template_hr = cv.imread('./../logos/logo_hr.png',0)
    template_vr = cv.imread('./../logos/logo_vr.png',0)
    template_vl = cv.imread('./../logos/logo_vl.png',0)
    
    orientations = ('hl','hr','vr','vl')
    templates = (template_hl, template_hr, template_vr, template_vl)

    gray = img

    found = None
      
    for i in range(len(templates)):

        (tH, tW) = templates[i].shape
       
        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 5)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = float(gray.shape[1]) / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            #edged = cv.Canny(resized, 50, 200)
            edged = resized
            result = cv.matchTemplate(edged, templates[i], cv.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv.minMaxLoc(result)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r, i)
                
    if False:
        print('not found with scaling')

    else:
        print(orientations[found[3]])
        
        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (maxVal, maxLoc, r, _) = found
        print(maxVal)
        print('---------')
        # rotate img
        if orientations[found[3]] == 'vr':
            img_lic, img_date, img_vin = find_logo_scale_rotation_v1(img, 'vr')

        elif orientations[found[3]] == 'vl':
            img_lic, img_date, img_vin = find_logo_scale_rotation_v1(img, 'vl')

        elif orientations[found[3]] == 'hr':
            img_lic, img_date, img_vin = find_logo_scale_rotation_v1(img, 'hr')
        else:
            img_lic, img_date, img_vin = find_logo_scale_rotation_v1(img, 'hl')
            
        return img_lic, img_date, img_vin
    

def find_logo_scale_rotation_v1(img, orientation):
    template = cv.imread('./../logos/logo_hl.png',0)
    
    if orientation == 'vr':
            img = cv.flip(img, 1)
            img = cv.transpose(img)

    elif orientation == 'vl':
        img = cv.flip(img, 0)
        img = cv.transpose(img)

    elif orientation == 'hr':
        img = cv.flip(img, -1)
        
    #img = skew_image(img)
    #img = find_best_angle(img)
    
    gray = img
    #show_wait_destroy('aa',gray)
    found = None
    visualize = True
    
    (tH, tW) = template.shape

    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 5)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
        r = float(gray.shape[1]) / float(resized.shape[1])

        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        # detect edges in the resized, grayscale image and apply template
        # matching to find the template in the image
        #edged = cv.Canny(resized, 50, 200)
        edged = resized
        result = cv.matchTemplate(edged, template, cv.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv.minMaxLoc(result)

        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r, 0)
                                      
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, maxLoc, r, _) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    
    img_lic, img_date, img_vin = find_bounding_boxes_fixed(img, (startX, startY), tW, tH, 60,ratio = r)

    # draw a bounding box around the detected result and display the image
    cv.rectangle(img, (startX, startY), (endX, endY), (0, 0, 255), 10)
    #show_wait_destroy_3d('fin', img)
    return img_lic, img_date, img_vin


def find_orientation_threshold_rotate(img):
    
    img = find_best_angle(img)
    img = extract_lines(img)
    template_hl = cv.imread('./../logos/logo_hl.png',0)
    template_hr = cv.imread('./../logos/logo_hr.png',0)
    template_vr = cv.imread('./../logos/logo_vr.png',0)
    template_vl = cv.imread('./../logos/logo_vl.png',0)
    
    orientations = ('hl','hr','vr','vl')
    templates = (template_hl, template_hr, template_vr, template_vl)

    #img = convert_to_3channels(img)
    max_matchtemplate_values = []
    meth = 'cv.TM_CCOEFF_NORMED'
    method = eval(meth)
    for template in templates:
        #img3 = img2.copy()

        w, h = template.shape[::-1]
        
        # Apply template Matching
        res = cv.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        max_matchtemplate_values.append(max_val)     
        
    ind = max_matchtemplate_values.index(max(max_matchtemplate_values))

    if max(max_matchtemplate_values) < 0.5:
        print('logo not found, trying with scaling')

        img_lic, img_date, img_vin = find_logo_scale_rotation(img)
    
    else:      
        # rotate img
        if orientations[ind] == 'vr':
            img = cv.flip(img, 1)
            img = cv.transpose(img)
            
        elif orientations[ind] == 'vl':
            img = cv.flip(img, 0)
            img = cv.transpose(img)
        
        elif orientations[ind] == 'hr':
            img = cv.flip(img, -1)
            #img = cv.transpose(img)
    
        # proceed with the best logo
        w, h = templates[0].shape[::-1]
        res = cv.matchTemplate(img,templates[0],method)
        threshold = 0.5
        loc = np.where( res >= threshold)
       
        print(str(orientations[ind]) + ' ' + str(max_matchtemplate_values[ind]))
        best_result = list(zip(*loc[::-1]))[0]
        
        cv.rectangle(img, best_result, (best_result[0] + w, best_result[1] + h), 0, 10)
        img_lic, img_date, img_vin =  find_bounding_boxes_fixed(img, best_result, w, h)
        
        #show_wait_destroy('final',img)
        
    return img_lic, img_date, img_vin


def gauss_otsu_thresholding(img):
    #blur = cv.GaussianBlur(img,(3,3),0)
    blur = img
    ret,thresh_img = cv.threshold(blur, 0, 255, cv.THRESH_OTSU)

    #show_wait_destroy_particular('gauss_otsu', thresh_img)
    return thresh_img


def remove_small_components(img):
    img=img.astype(np.uint8) 
    img = cv.bitwise_not(img)

    #show_wait_destroy_particular('reverse',img)
    #find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv.connectedComponentsWithStats(img, connectivity=8)
    #connectedComponentswithStats yields every seperated component with information on each of them, such as size
    #the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
    sizes = stats[1:, -1]; nb_components = nb_components - 1

    # minimum size of particles we want to keep (number of pixels)
    #here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
    min_size = 40 

    #your answer image
    img2 = np.zeros((output.shape), dtype=np.uint8)
    #for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            img2[output == i + 1] = 255

    #
    #show_wait_destroy_particular('removed_particles',img2)
    img2 = cv.bitwise_not(img2)
    #show_wait_destroy_particular('removed_particles_bit',img2)
    return img2


def erode_and_dilate(img):
    erodeStructure = cv.getStructuringElement(cv.MORPH_OPEN, (3,3))
    res2 = cv.erode(img, erodeStructure, iterations=2)
    #show_wait_destroy_particular('erosion', res2)
    dilatationStructure = cv.getStructuringElement(cv.MORPH_DILATE, (3,3))
    res2 = cv.dilate(res2, dilatationStructure, iterations=2)
    #show_wait_destroy_particular('dilatation', res2)
    
    
