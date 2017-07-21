import os, sys, string
import random
import cv2
import numpy as np
from imgproc import *
import ConfigParser
import math
import multiprocessing

MODE = ["BLUR", "JITTER", "COMPRESS", "NOISE", "PNG_MERGE"]

class Generator():
    def __init__(self, conf_path):
        #load conf
        if not os.path.exists(conf_path):
            print "-> conf file not exist, check conf path."
            sys.exit()
        conf = ConfigParser.ConfigParser()
        conf.read(conf_path)
        #parse BASIC
        self.mode = conf.get("BASIC", "mode")
        if self.mode not in MODE:
            print "-> mode name error, mode name should in {}".format(MODE)
            sys.exit()
        self.input_list = conf.get("BASIC", "input_list")
        if not os.path.exists(self.input_list):
            print "-> input_list not exist, check path."
            sys.exit()

        self.output_folder = conf.get("BASIC", "output_folder")
        if not os.path.exists(self.output_folder):
            os.system("mkdir -p " + self.output_folder)
        self.processor_num = conf.getint("BASIC", "processor_num")
        print self.processor_num
        #parse mode
        if self.mode == "BLUR":
            self.large_scale = conf.getboolean("BLUR", "large_scale")
            self.thres = conf.getint("BLUR", "thres")
        if self.mode == "JITTER":
            self.add_num = conf.getint("JITTER", "add_num")
            self.thres = conf.getint("JITTER", "thres")
        if self.mode == "COMPRESS":
            self.thres = conf.getint("COMPRESS", "thres")
        if self.mode == "NOISE":
            self.thres = conf.getfloat("NOISE", "thres")
        if self.mode == "PNG_MERGE":
            pass
        print "-> conf parse success."

    def proc_batch(self, image_list, func, params):
        for file in image_list[0]:
            print file
            image = cv2.imread(file)
            if image == None:
                continue
            result_name = "{}/{}_{}_{}.jpg".format(self.output_folder, file.split("/")[-1].split(".")[0], self.mode, self.thres)
            result = func(image, *params)
            cv2.imwrite(result_name, result)

    def generate(self):
        all_image_path = []
        with open(self.input_list) as file:
            for line in file.readlines():
                all_image_path.append(line.strip())          
        part_num = int(math.ceil(1.0 * len(all_image_path) / self.processor_num))
        records = []   
        for i in xrange(self.processor_num):
            part_list = all_image_path[i * part_num : (i + 1) * part_num]
            if self.mode == "BLUR":
                params = [self.thres, self.large_scale]
                process = multiprocessing.Process(target = self.proc_batch, args=([part_list], rand_blur, params))
            if self.mode == "JITTER":
                params = [self.add_num, self.thres]
                process = multiprocessing.Process(target = self.proc_batch, args=([part_list], rand_jitters, params))
            if self.mode == "COMPRESS":
                params = [self.thres]
                process = multiprocessing.Process(target = self.proc_batch, args=([part_list], jpeg_compression, params))
            if self.mode == "NOISE":
                params = [self.thres]
                process = multiprocessing.Process(target = self.proc_batch, args=([part_list], add_salt_noise, params))
            if self.mode == "PNG_MERGE":
                params = ()
                process = multiprocessing.Process(target = self.proc_batch, args=([part_list], add_png_image, params))
            process.start()
            records.append(process)
        for process in records:
            process.join()

if __name__ == "__main__":
    gen = Generator("preprocess.conf")
    gen.generate()

