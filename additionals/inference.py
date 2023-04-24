import additionals.globals as gv
import cv2
import torch
import time
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

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
        # initialize TensorRT engine and parse ONNX model
        builder = trt.Builder(trt.Logger())
        network = builder.create_network()
        parser = trt.OnnxParser(network, trt.Logger())

        # allow TensorRT to use up to 1GB of GPU memory for tactic selection
        builder.max_workspace_size = 1 << 30
        # we have only one image in batch
        builder.max_batch_size = 1
        # use FP16 mode if possible
        if builder.platform_has_fast_fp16:
            builder.fp16_mode = True

        # parse ONNX
        with open(self.model_path, 'rb') as model:
            print('Beginning ONNX file parsing')
            parser.parse(model.read())
        print('Completed parsing of ONNX file')

        # generate TensorRT engine optimized for the target platform
        print('Building an engine...')
        engine = builder.build_cuda_engine(network)
        context = engine.create_execution_context()
        print("Completed creating Engine")
        return engine, context

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

    def preprocess_image(img_path):
        
        # read input image
        input_img = cv2.imread(img_path)
        # do transformations
        input_data = cv2.resize(input_img, (640, 640), interpolation=cv2.INTER_NEAREST)
        # prepare batch
        batch_data = torch.unsqueeze(input_data, 0)

        return batch_data

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
    
    def main(self):

        engine, context = self.build_engine()
        # get sizes of input and output and allocate memory required for input data and for output data
        for binding in engine:
            if engine.binding_is_input(binding):  # we expect only one input
                input_shape = engine.get_binding_shape(binding)
                input_size = trt.volume(input_shape) * engine.max_batch_size * np.dtype(np.float32).itemsize  # in bytes
                device_input = cuda.mem_alloc(input_size)
            else:  # and one output
                output_shape = engine.get_binding_shape(binding)
                # create page-locked memory buffers (i.e. won't be swapped to disk)
                host_output = cuda.pagelocked_empty(trt.volume(output_shape) * engine.max_batch_size, dtype=np.float32)
                device_output = cuda.mem_alloc(host_output.nbytes)

        # take image
        names = self.readnames()
        stream = cuda.Stream()
        video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        if video_capture.isOpened():
            try:
                while gv.DETECTION_RUNNING:
                    ret_val, frame = video_capture.read()
                    # Check to see if the user closed the window
                    # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                    # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # preprocess input data
                    host_input = np.array(self.preprocess_image("turkish_coffee.jpg").numpy(), dtype=np.float32, order='C')
                    
                    # run inference
                    context.execute_async(bindings=[int(device_input), int(device_output)], stream_handle=stream.handle)
                    cuda.memcpy_dtoh_async(host_output, device_output, stream)
                    stream.synchronize()

                    # postprocess results
                    boxes, scores, classes = torch.Tensor(host_output).reshape(engine.max_batch_size, output_shape[0])

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
