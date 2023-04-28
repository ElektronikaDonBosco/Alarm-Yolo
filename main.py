import threading
import telebot
import numpy as np
import additionals.globals as gv
import jetson_inference
import jetson_utils

net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson_utils.videoSource("csi://0")      # '/dev/video0' for V4L2
display = jetson_utils.videoOutput("display://0") # 'my_video.mp4' for file

detecting = False 
render_img = False
frame = None
thread1 = None

bot = telebot.TeleBot("6099780796:AAEg4EMmD2iuRe0LJvedPHSnsFLu1mfzY3c")

def tracking(message):
    global frame
    while gv.DETECTION_RUNNING:
        img = camera.Capture()
        detections = net.Detect(img)
        if render_img:
            display.Render(img)
            display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
        for detection in detections:
            detection.ClassID
            
        chat_id = message.chat.id
        bot.reply_to(message, "Pertsona dago")

@bot.message_handler(commands=['hasi', 'empezar', 'start'])
def send_welcome(message):
    bot.reply_to(message, """Ongi etorri bot honetara, idatzi /laguntza aukerak ikusteko
    Bienvenido a este bot, escribe /ayuda para ver la opciones
    Welcome to this bot, write /help to see the options""")

@bot.message_handler(commands=['laguntza'])
def laguntza(message):
    bot.reply_to(message, """Botoietako aukerak :-
    /piztu - martxan jartzeko
    /itzali - gelditzeko
    /argazkia - argazkia bidaltzeko""")

@bot.message_handler(commands=['ayuda'])
def laguntza(message):
    bot.reply_to(message, """Botoietako aukerak :-
    /encender - para poner en marcha
    /apagar - para parar
    /foto - para pedir foto""")

@bot.message_handler(commands=['help'])
def laguntza(message):
    bot.reply_to(message, """Botoietako aukerak :-
    /turn_on - to turn on
    /turn_off - to turn off
    /photo - to take a photo""")

@bot.message_handler(commands=['piztu', 'encender', 'turn_on'])
def piztu(message):
    global thread1
    gv.DETECTION_RUNNING = True
    thread1 = threading.Thread(target=tracking, args=(message,))
    thread1.start()
    bot.reply_to(message, "Piztu da - Se ha encendido - Turned on")

@bot.message_handler(commands=['itzali', 'apagar', 'turn_off'])
def itzali(message):
    global frame
    global thread1
    gv.DETECTION_RUNNING = False
    thread1.stop()
    frame = None
    bot.reply_to(message, message.text)

@bot.message_handler(commands=['argazkia', 'foto', 'photo'])
def argazkia(message):
    global frame
    chat_id = message.chat.id
    bot.send_photo(chat_id, "https://github.com/mikelalda/Alarm-Yolo/raw/master/assets/20230412_120813_Screenshot-2022-12-16-092357.png")
    bot.send_photo(chat_id, "FILEID")

client = None


def main():
    global bot
    
    print('Empezar bot')
    bot.polling()
    
if __name__ == '__main__':
    main()
