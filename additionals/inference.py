import additionals.globals as gv
import cv2
import torch
import time
import numpy as np
import tensorrt as trt
from PIL import Image
from collections import OrderedDict,namedtuple
import os
import random

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

class Inference ():
    def __init__(self,model_path):
        self.model_path = model_path

    def __call__(self):
        self.main()

    def readnames(self):
        names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 
                    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 
                    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 
                    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 
                    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 
                    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 
                    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 
                    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 
                    'hair drier', 'toothbrush']

        return names
        
    def loadmodel(self):
        w = self.model_path if os.path.isfile(self.model_path) else './yolov7-tiny-nms.trt'
        device = torch.device('cuda:0')

        # Infer TensorRT Engine
        Binding = namedtuple('Binding', ('name', 'dtype', 'shape', 'data', 'ptr'))
        logger = trt.Logger(trt.Logger.INFO)
        trt.init_libnvinfer_plugins(logger, namespace="")
        with open(w, 'rb') as f, trt.Runtime(logger) as runtime:
            model = runtime.deserialize_cuda_engine(f.read())
            print(model)
        bindings = OrderedDict()
        for index in range(model.num_bindings):
            name = model.get_binding_name(index)
            dtype = trt.nptype(model.get_binding_dtype(index))
            shape = tuple(model.get_binding_shape(index))
            data = torch.from_numpy(np.empty(shape, dtype=np.dtype(dtype))).to(device)
            bindings[name] = Binding(name, dtype, shape, data, int(data.data_ptr()))
        binding_addrs = OrderedDict((n, d.ptr) for n, d in bindings.items())
        context = model.create_execution_context()
        return bindings, binding_addrs, context, device

    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, r, (dw, dh)

    def postprocess(self, boxes,r,dwdh):
        dwdh = torch.tensor(dwdh*2).to(boxes.device)
        boxes -= dwdh
        boxes /= r
        return boxes

    def preprocess(self, img, device):
        image = img.copy()
        image, ratio, dwdh = self.letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)

        im = image.astype(np.float32)
        im.shape

        im = torch.from_numpy(im).to(device)
        im/=255
        im.shape
        return im, ratio, dwdh

    def predict(self, im, binding_addrs, context, bindings):
        start = time.perf_counter()
        binding_addrs['images'] = int(im.data_ptr())
        context.execute_v2(list(binding_addrs.values()))
        print(f'Cost {time.perf_counter()-start} s')

        nums = bindings['num_dets'].data
        boxes = bindings['det_boxes'].data
        scores = bindings['det_scores'].data
        classes = bindings['det_classes'].data
        nums.shape,boxes.shape,scores.shape,classes.shape

        boxes = boxes[0,:nums[0][0]]
        scores = scores[0,:nums[0][0]]
        classes = classes[0,:nums[0][0]]
        return boxes, scores, classes

    def drawdata(self, im, boxes, scores, classes, names, colors, ratio, dwdh):
        for box,score,cl in zip(boxes,scores,classes):
            box = self.postprocess(box,ratio,dwdh).round().int()
            name = names[cl]
            color = colors[name]
            name += ' ' + str(round(float(score),3))
            cv2.rectangle(im,box[:2].tolist(),box[2:].tolist(),color,2)
            cv2.putText(im,name,(int(box[0]), int(box[1]) - 2),cv2.FONT_HERSHEY_SIMPLEX,0.75,color,thickness=2)

        return Image.fromarray(im)
    
    def main(self):

        bindings, binding_addrs, context, device = self.loadmodel()
        names = self.readnames()
        # colors = {name:[random.randint(0, 255) for _ in range(3)] for i,name in enumerate(names)}

        # warmup for 10 times
        for _ in range(10):
            tmp = torch.randn(1,3,640,640).to(device)
            binding_addrs['images'] = int(tmp.data_ptr())
            context.execute_v2(list(binding_addrs.values()))

        # take image
        video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        if video_capture.isOpened():
            try:
                while gv.DETECTION_RUNNING:
                    ret_val, frame = video_capture.read()
                    # Check to see if the user closed the window
                    # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                    # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    im, ratio, dwdh = self.preprocess(img, device)
                    
                    boxes, scores, classes = self.predict(im, binding_addrs, context, bindings)

                    for det in classes:
                        if det == 0 or det == names[0]:
                            gv.PERSON_DETECTED = True
                            return frame
                        else:
                            gv.PERSON_DETECTED = False
                            return None

            finally:
                video_capture.release()
        else:
            print("Error: Unable to open camera")

        # result = self.drawdata(im, boxes, scores, classes, names, colors, ratio, dwdh)
