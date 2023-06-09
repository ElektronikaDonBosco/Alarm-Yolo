import threading
import telebot
import numpy as np
import additionals.globals as gv
import jetson.inference
import jetson.utils

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("/dev/video0")  #for V4L2 else 'csi://0' for csi
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file

detecting = False 
render_img = False # False=do not see camera image at screen. True=See camera image at screen.
frame = None

bot = telebot.TeleBot("6068562840:AAHi7Oq9fXq3F3IiZXm-f0VuZ-s6p8sx8Hk", parse_mode=None) #insert here the API KEY provided by bot at Telegram


def tracking(message):
    while gv.DETECTION_RUNNING:
        frame = camera.Capture()
        detections = net.Detect(frame)
        if render_img:
            display.Render(frame)
            display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
        for detection in detections:
            if detection.ClassID == 1:
                bot.send_message(message.chat.id, "Pertsona/Persona/Person") # this is the message displayed at Telegram

#Messages that will be displayed at Telegram
@bot.message_handler(commands=['hasi', 'empezar', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Ongi etorri bot honetara, idatzi /laguntza aukerak ikusteko
    Bienvenido a este bot, escribe /ayuda para ver la opciones
    Welcome to this bot, write /help to see the options""")

@bot.message_handler(commands=['laguntza'])
def laguntza(message):
    bot.send_message(message.chat.id, """Botoietako aukerak :-
    /piztu - martxan jartzeko
    /itzali - gelditzeko""")

@bot.message_handler(commands=['ayuda'])
def laguntza(message):
    bot.send_message(message.chat.id, """Botoietako aukerak :-
    /encender - para poner en marcha
    /apagar - para parar""")

@bot.message_handler(commands=['help'])
def laguntza(message):
    bot.send_message(message.chat.id, """Botoietako aukerak :-
    /turn_on - to turn on
    /turn_off - to turn off""")

@bot.message_handler(commands=['piztu', 'encender', 'turn_on'])
def piztu(message):
    gv.DETECTION_RUNNING = True
    thread1 = threading.Thread(target=tracking, args=(message,))
    thread1.start()
    bot.send_message(message.chat.id, "Piztu da - Se ha encendido - Turned on")

@bot.message_handler(commands=['itzali', 'apagar', 'turn_off'])
def itzali(message):
    gv.DETECTION_RUNNING = False
    bot.send_message(message.chat.id,"Itzali da - Se ha apagado - Turned off")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

def main():
    global bot
    
    print('Empezar bot...')
    bot.polling()
    print('Apagando bot...')
    
if __name__ == '__main__':
    main()
