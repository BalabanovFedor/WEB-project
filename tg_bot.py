from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import requests
from main import server

TOKEN = "901380312:AAG0I0BeWrldYTUXQc0JWU2oZU7rtgA-F7I"


def start(update, context):
    update.message.reply_text('начнем')


def help(update, context):
    t = """/init <school> <class> -- для начала работы укажите школу и класс (можно изменить в любой момент)
    /get <subject> <completion_date:YYYY-MM-DD> -- выведет задания указанных предметов и чисел (параметры необязательные)
    """
    update.message.reply_text(t)


def view_class(update, context):
    clases = requests.get(server + "/api/clas").json()
    if clases['clas']:
        clases = sorted(clases['clas'], key=lambda i: i['school'])
        text = ''
        for item in clases:
            text += f"Школа: {item['school']}, класс: {item['name']}\n"
        update.message.reply_text(text)
    else:
        update.message.reply_text("Не могу найти класс или недоступен сервер")


def init(update, context):
    mtext = update.message.text.split()
    if len(mtext) < 3:
        update.message.reply_text("Не указана школа или класс")
    school, clas = mtext[1:]

    clases = requests.get(server + "/api/clas").json()
    # print(clases)
    clas_id = None
    if clases['clas']:
        for item in clases['clas']:
            if item['name'] == clas and item['school'] == school:
                clas_id = item['id']
                context.user_data['clas_id'] = clas_id
                update.message.reply_text("Успешно!")
        if not clas_id:
            update.message.reply_text(
                "Не могу найти класс. Вызовите команду /view_class чтобы увидеть все классы системы.")
    else:
        update.message.reply_text("Не могу найти класс или недоступен сервер")


# вернет задания, параметры: предмет, число
def get(update, context):
    update.message.reply_text(context.user_data['clas_id'])


def msg_handler(update, context):
    pass


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('get', get, pass_user_data=True, pass_args=True))
    dp.add_handler(CommandHandler("init", init, pass_user_data=True, pass_args=True))
    dp.add_handler(CommandHandler('view_class', view_class))

    msgs = MessageHandler(Filters.text, msg_handler, pass_user_data=True, pass_chat_data=True)
    dp.add_handler(msgs)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
