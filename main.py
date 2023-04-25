import additionals.globals as gv
import argparse
import threading
import telebot
from elements.yolo import OBJ_DETECTION

import cv2
import numpy as np

frame = None
chat_id = ''

bot = telebot.TeleBot("6099780796:AAEg4EMmD2iuRe0LJvedPHSnsFLu1mfzY3c")

def tracking():
    global frame
    global chat_id

    while gv.DETECTION_RUNNING:
        frame = inference()
        if gv.PERSON_DETECTED:
            bot.send_message(chat_id, "Pertsona dago")

@bot.message_handler(commands=['hasi', 'empezar', 'start'])
def send_welcome(message):
    global chat_id
    chat_id = message[-1].chat.id
    bot.reply_to(message, """Ongi etorri bot honetara, idatzi /laguntza aukerak ikusteko
    Bienvenido a este bot, escribe /ayuda para ver la opciones
    Welcome to this bot, write /help to see the options""")

@bot.message_handler(commands=['laguntza', 'ayuda', 'help'])
def laguntza(message):
    bot.reply_to(message, """Botoietako aukerak :-
    /piztu - martxan jartzeko
    /itzali - gelditzeko""")

@bot.message_handler(commands=['piztu', 'encender', 'turn_on'])
def piztu(message):
    global thread1
    gv.DETECTION_RUNNING = True
    thread1.start()
    bot.reply_to(message, "Piztu da - Se ha encendido - Turned on")

@bot.message_handler(commands=['itzali', 'apagar', 'turn_off'])
def itzali(message):
    global frame
    global thread1
    thread1.stop()
    gv.DETECTION_RUNNING = False
    frame = None
    bot.reply_to(message, message.text)

@bot.message_handler(commands=['argazkia', 'foto', 'photo'])
def argazkia(message):
    global frame
    global chat_id
    bot.send_photo(chat_id, frame)
    bot.send_photo(chat_id, "FILEID")

client = None

thread1 = threading.Thread(target=tracking)


Object_classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
                'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
                'hair drier', 'toothbrush' ]

Object_colors = list(np.random.rand(80,3)*255)
Object_detector = OBJ_DETECTION('weights/yolov5s.pt', Object_classes)

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


# To flip the image, modify the flip_method parameter (0 and 2 are the most common)
print(gstreamer_pipeline(flip_method=0))
def inference():
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        while gv.DETECTION_RUNNING:
            ret, frame = cap.read()
            if ret:
                # detection process
                objs = Object_detector.detect(frame)

                # plotting
                for obj in objs:
                    
                    label = obj['label']
                    if 0 == Object_classes[0].index(label):
                        gv.PERSON_DETECTED = True
                        return frame
        cap.release()
    else:
        print("Unable to open camera")


def main():
    global bot
    
    print('Empezar bot')
    bot.polling()
    
if __name__ == '__main__':
    main()