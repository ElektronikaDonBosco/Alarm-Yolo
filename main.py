import additionals.inference as infer
import additionals.globals as gv
import cv2
import torch
import random
import argparse
from telegram import *
from telegram.ext import *

class GlobalChange(object):
    def __init__(self):
        self._global_data = 10.0
        self._observers = []

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, value):
        self._global_data = value
        for callback in self._observers:
            print('announcing change')
            callback(self._global_data)

    def bind_to(self, callback):
        print('bound')
        self._observers.append(callback)

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
    gv.DETECTION_RUNNING = True
    update.message.reply_text("Piztu da")

def itzali(update: Update, context: CallbackContext):
    gv.DETECTION_RUNNING = False
    update.message.reply_text("Itzali da")

def argazkia(update: Update, context: CallbackContext):
    gv.DETECTION_RUNNING = False
    update.message.reply_text("Argazkia bidali da")

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
    
def main(model_path, classnames_path):
    infer(model_path, classnames_path)

    data = GlobalChange()
    data.bind_to(argazkia)

    updater = Updater(token="2115883750:AAGqskwSwvRD8iQlFA8vn9rUKG7DY8qM-jg")
    dispatcher = updater.dispatcher

    text_laguntza = "/laguntza"
    text_piztu = "/piztu"
    text_itzali = "/itzali"
    text_konektatu = "/konektatuta?"

    client = None

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
                        help='the path to workspace')
    args = parser.parse_args()

    main(args.model_path, args.classnames_path)
