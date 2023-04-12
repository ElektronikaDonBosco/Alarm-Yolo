import additionals.inference as infer
import additionals.globals as gv
import cv2
import torch
import random
import argparse
import threading
from telegram import *
from telegram.ext import *

frame = None
inference = None
chat_id = ''

text_laguntza = "/laguntza"
text_piztu = "/piztu"
text_itzali = "/itzali"
text_konektatu = "/konektatuta?"

client = None

def tracking(update: Update, context: CallbackContext):
    global frame
    global inference
    global chat_id
    while gv.DETECTION_RUNNING:
        frame = inference.next()
        update.message.reply_text("Pertsona dago")

thread1 = threading.Thread(target=tracking)

def startCommand(update: Update, context: CallbackContext):
    buttons = [[KeyboardButton(text_laguntza),KeyboardButton(text_konektatu)]
               ,[KeyboardButton(text_piztu),KeyboardButton(text_itzali)]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ongi etorri bot honetara, eman /laguntza akzioak ikusteko", reply_markup=ReplyKeyboardMarkup(buttons))


def laguntza(update: Update, context: CallbackContext):
    update.message.reply_text("""Botoietako aukerak :-
    /konektatu - PLCra konektatu
    /piztu - irteerak 1era jartzeko
    /itzali - irteerak 0era itzaltzeko""")

def connect(update: Update, context: CallbackContext):
    update.message.reply_text("Konektatuta dago")

def piztu(update: Update, context: CallbackContext):
    global thread1
    gv.DETECTION_RUNNING = True
    thread1.start()
    update.message.reply_text("Piztu da")

def itzali(update: Update, context: CallbackContext):
    global frame
    global thread1
    thread1.stop()
    gv.DETECTION_RUNNING = False
    frame = None
    update.message.reply_text("Itzali da")

def argazkia(update: Update, context: CallbackContext):
    global frame
    if frame != None:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=frame)
        update.message.reply_text("Argazkia bidali da")
    else:
        update.message.reply_text("Ez dago argazkirik, beraz ez da bidali")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
    
def main(model_path, classnames_path):
    global inference

    inference = infer(model_path, classnames_path)

    updater = Updater(token="6099780796:AAEg4EMmD2iuRe0LJvedPHSnsFLu1mfzY3c")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("hasi", startCommand))
    updater.dispatcher.add_handler(CommandHandler('konektatu', connect))
    updater.dispatcher.add_handler(CommandHandler('piztu', piztu))
    updater.dispatcher.add_handler(CommandHandler('laguntza', laguntza))
    updater.dispatcher.add_handler(CommandHandler('itzali', itzali))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_text))  # Filters out unknown commands

    # Filters out unknown messages.
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

    updater.start_polling()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--model_path', metavar='path', required=True,
                        help='the path to model')
    args = parser.parse_args()

    main(args.model_path, args.classnames_path)
