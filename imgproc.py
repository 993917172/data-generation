import cv2
import numpy as np
import random

def random_jitters(image, add_num, thres):
    """
    input: image, add_num, thres (normally between [0, 5])
    output: image with random jitters (image size change)
    description: multiple images added with weights to generate jitter effects
    """
    h, w, c = image.shape
    print image.shape
    base_roi = image[thres : h - thres, thres : w - thres, :]
    random_seed = [random.randint(-1 * thres, thres) for i in xrange(2 * add_num)]

    weight = 1.0 / add_num
    result = np.zeros(base_roi.shape)
    for i in xrange(add_num):
        result += weight * image[thres + random_seed[i] : h - thres + random_seed[i], 
                thres + random_seed[add_num + i] : w - thres + random_seed[add_num + i], :]
    return result

def add_rand_blur(image, thres):
    """
    input: image, thres (value)
    output: image with random blur (image size unchange)
    description: if need large scale blur, directly downsample and upsample
    """

def add_salt_noise(image ,thres):
    """
    input: image, thres (add salt noise degree)
    output: image with salt noise (image size unchange)
    description: null
    """

def jpeg_compression(image, thres):
    """
    input: image, thres()
    output: image with jpeg compression
    description: null
    """
    if thres < 0 or thres > 100:
        print "-> jpeg compression thres error, value should between [0-100]"
        return None
    flag, result = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, thres])
    return cv2.imdecode(result, cv2.CV_LOAD_IMAGE_COLOR)

def check_border(original_size, check_bbox):
    """
    check whether bboxs satisfy image size constrain
    """
    width, height = original_size
    l, t, w, h = check_bbox
    if w <= 0 or h <= 0 or l < 0 or l >= width or t < 0 or t >= height:
        return False
    if l + w >= width or t + h > height:
        return False
    return True

def rand_rescale(image, low_thres):
    """
    rescale image with random ratio, only downsample
    """
    if low_thres > 1.0 or low_thres < 0:
        print "Random rescale thres error."
        return None
    scale = random.uniform(low_thres, 1.0)
    h, w, c = image.shape
    image_rescale = cv2.resize(image, (int(scale * w), int(scale * h)))
    return image_rescale

def add_png_image(image, png_image, roi):
    """
    input: image, png_image(with alpha channel), roi (left, top, width, height)
    output: image merged with png image
    description: add png image like watermark to original image
    """
    h, w, c = image.shape
    h_png, w_png, c_png = png_image.shape
    if c != 3 or c_png != 4:
        print "-> Input image channel num not equals 3, png_image channel num not equals 4."
        return None
    else:
        print "image size: {}".format([h, w, c])
        print "png_image size: {}".format([h_png, w_png, c_png])
        print "roi(l t w h): {}".format(roi)
    if not check_border([w, h], roi):
        print "-> ROI border check failed."
        return None
    #check png image size and roi size
    protect_margin = 3 # protect for border cross
    if w_png > roi[2] or h_png > roi[3]:
        print "-> png image size larger than roi area, need resize"
        ratio_w = 1.0 * w_png / roi[2]
        ratio_h = 1.0 * h_png / roi[3]
        ratio = ratio_w if ratio_w > ratio_h else ratio_h
        png_image = cv2.resize(png_image, (int(w_png / ratio) - 2 * protect_margin\
            , int(h_png / ratio) - 2 * protect_margin)) #protect margin may cause a bug, not seriously
    #random watermark size
    png_randsize = rand_rescale(png_image, 0.5) # hyper-param
    #random watermark optic
    optic_ratio = random.uniform(0.2, 1) # hyper-param
    #random positon in crop patch
    h_png, w_png, c_png = png_randsize.shape
    roi_pos_center = [int(roi[0] + roi[2] / 2), int(roi[1] + roi[3] / 2)]  
    diff_margin = [int(roi[2] / 2 - w_png / 2), int(roi[3] / 2 - h_png / 2)]
    print "roi_pos_center: {}".format(roi_pos_center)
    print "diff margin: {}".format(diff_margin)
    rand_pos_center = [random.randint(int(roi_pos_center[0] - diff_margin[0] + protect_margin),\
        int(roi_pos_center[0] + diff_margin[0] - protect_margin)),\
        random.randint(int(roi_pos_center[1] - diff_margin[1] + protect_margin),\
        int(roi_pos_center[1] + diff_margin[1] - protect_margin))]
    #merge image and png_randsize
    image = np.float32(image)
    png_randsize = np.float32(png_randsize)
    result = image.copy()
    pos_start_x = int(rand_pos_center[0] - w_png / 2.0)
    pos_start_y = int(rand_pos_center[1] - h_png / 2.0)
    print "w_png: {}".format(w_png)
    print "h_png: {}".format(h_png)
    print "pos_start_x: {}".format(pos_start_x)
    print "pos_start_y: {}".format(pos_start_y)
    for i in xrange(0, h_png):
        for j in xrange(0, w_png):
            # alpha channel decide weights
            if png_randsize[i, j, 3] != 0:
                result[i + pos_start_y, j + pos_start_x] = \
                optic_ratio * png_randsize[i, j, 3] / 225.0 * png_randsize[i, j , 0 : 3] + \
                (1 - optic_ratio * png_randsize[i, j, 3] / 225.0 ) * image[i + pos_start_y, j + pos_start_x]  
    return result

if __name__ == "__main__":
    count = 0
    while(count < 1):
        count += 1
#select model to test
        enable_module = "jpeg"
#load test image
        image = cv2.imread("test.jpg")
#process
        if enable_module == "jitter":
            result = random_jitters(image, 2, 5)
        elif enable_module == "blur":
            pass
        elif enable_module == "salt":
            pass
        elif enable_module == "jpeg": 
            result = jpeg_compression(image, 50)
        elif enable_module == "add_png":
            png_image = cv2.imread("sohu-big.png", cv2.IMREAD_UNCHANGED)
            h, w, c = image.shape
            result = add_png_image(image, png_image, [int(w * 0.1), 0, int(w * 0.8), int(h * 0.8)])
#write image file
        cv2.imwrite("test_result_{}.jpg".format(count), result)
