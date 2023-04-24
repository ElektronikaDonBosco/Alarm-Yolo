from additionals.inference import Inference as infer
import additionals.globals as gv
import argparse
import threading
import telebot

frame = None
inference = None
chat_id = ''

bot = telebot.TeleBot("6099780796:AAEg4EMmD2iuRe0LJvedPHSnsFLu1mfzY3c")

def tracking():
    global frame
    global inference
    global chat_id

    while gv.DETECTION_RUNNING:
        frame = inference.main()
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
    
def main(model_path):
    global inference
    global bot

    print('Cargar modelo')
    inference = infer(model_path)
    inference.build_engine()
    
    print('Empezar bot')
    bot.polling()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--model_path', required=True,
                        help='the path to model')
    args = parser.parse_args()

    main(args.model_path)
