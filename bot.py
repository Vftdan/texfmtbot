from telebot import TeleBot, apihelper
import json
from texfmt import tex2html, TexException

conf = json.load(open('priv.json'))
bot = TeleBot(conf['key'])
apihelper.proxy = conf.get('proxy', apihelper.proxy)

def stripcmd(txt):
    if txt == '' or txt[0] != '/':
        return txt
    return ' '.join(txt.split(' ')[1:])

@bot.message_handler(commands=['tex'])
def texfmt(msg):
    try:
        try:
            bot.reply_to(msg, tex2html(stripcmd(msg.text), True), parse_mode='HTML')
        except TexException as e:
            bot.reply_to(msg, str(e))
        except BaseException as e:
            bot.reply_to(msg, 'Error occured')
            print(e)
    except BaseException as e:
        print(e)

bot.polling()
