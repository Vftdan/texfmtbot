#! /usr/bin/env python3
from telebot import TeleBot, apihelper
from telebot.types import InlineQueryResultArticle as IQRA
from telebot.types import InputTextMessageContent as ITMC
import json
from texfmt import tex2html, TexException

conf = json.load(open('priv.json'))
bot = TeleBot(conf['key'])
apihelper.proxy = conf.get('proxy', apihelper.proxy)

def Constant(c):
    def f(*args, **kwargs):
        return c
    return f

def stripcmd(txt):
    if txt == '' or txt[0] != '/':
        return txt
    return ' '.join(txt.split(' ')[1:])

def nohtml(html):
    ents = {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"'}
    mode_ent = False
    mode_tag = False
    res = []
    ent = ''
    for c in html:
        if mode_tag:
            if c == '>':
                mode_tag = False
            continue
        if mode_ent:
            if c == ';':
                mode_ent = False
                res.append(ents.get(ent, '&{0};'.format(ent)))
                ent = ''
                continue
            ent += c
            continue
        if c == '&':
            mode_ent = True
            continue
        if c == '<':
            mode_tag = True
            continue
        res.append(c)
    return ''.join(res)

@bot.message_handler(commands=['tex'])
def texcmd(msg):
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

@bot.inline_handler(Constant(True))
def inlinequeryhandler(iq):
    try:
        if len(iq.query) == 0:
            return
        result = tex2html(stripcmd(iq.query), True)
        bot.answer_inline_query(iq.id, [
            IQRA('1', 'TeX format', ITMC(result, parse_mode='HTML'), description=nohtml(result))
            ])
    except BaseException as e:
        pass

bot.polling()
