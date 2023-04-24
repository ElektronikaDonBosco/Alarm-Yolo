import additionals.inference as infer
import additionals.globals as gv
import argparse
import threading
from telegram.ext import Updater, CommandHandler

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
        if gv.PERSON_DETECTED:
            update.message.reply_text("Pertsona dago")

thread1 = threading.Thread(target=tracking)

def startCommand(update, context):
    buttons = [[KeyboardButton(text_laguntza)]
               ,[KeyboardButton(text_piztu),KeyboardButton(text_itzali)]]
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Ongi etorri bot honetara. Bot honek etxeko alarma bat kontrolatzen du, pertsonarik sartu den edo ez ikusteko. Eman /laguntza akzioak ikusteko",
                             reply_markup=ReplyKeyboardMarkup(buttons))


def laguntza(update, context):
    update.message.reply_text("""Botoietako aukerak :
    /piztu - Alarma martxan jartzeko
    /itzali - Alarma itzaltzeko""")

def piztu(update, context):
    global thread1
    gv.DETECTION_RUNNING = True
    thread1.start()
    update.message.reply_text("Piztu da")

def itzali(update, context):
    global frame
    global thread1
    thread1.stop()
    gv.DETECTION_RUNNING = False
    frame = None
    update.message.reply_text("Itzali da")

def argazkia(update, context):
    global frame
    if frame != None:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=frame)
        update.message.reply_text("Argazkia bidali da")
    else:
        update.message.reply_text("Ez dago argazkirik, beraz ez da bidali")

def error(update, context):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update, context):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
    
def main(model_path):
    global inference

    inference = infer(model_path)

    updater = Updater("6099780796:AAEg4EMmD2iuRe0LJvedPHSnsFLu1mfzY3c")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("hasi", startCommand))
    dispatcher.add_handler(CommandHandler('piztu', piztu))
    dispatcher.add_handler(CommandHandler('laguntza', laguntza))
    dispatcher.add_handler(CommandHandler('itzali', itzali))
    dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--model_path', value='models/yolov7-tiny-nms.trt', metavar='path', required=True,
                        help='the path to model')
    args = parser.parse_args()

    main(args.model_path)
