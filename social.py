#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import log_on_fail, splitCommand, matchKey
import yaml
import os
from os import path
from db import DB
import random
import sys

LIMIT = 10

test_usr = 'b4cxb'

if 'chinese' in str(sys.argv):
    lan = 'zh'
else:
    lan = 'en'
db = DB(lan)

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

with open(lan + '_string') as f:
    strings = yaml.load(f, Loader=yaml.FullLoader)

with open('ban') as f:
    ban = yaml.load(f, Loader=yaml.FullLoader)

updater = Updater(credential[lan + '_token'], use_context=True)
tele = updater.bot
debug_group = tele.get_chat(-1001198682178)

def askNext(usr, msg):
    idx = db.getQuestionIndex(usr, ask=True)
    if idx == float('Inf'):
        return msg.reply_text(strings['h2'])
    msg.reply_text(strings['q' + idx])

@log_on_fail(debug_group)
def handlePrivate(update, context):
    global ban
    usr = update.effective_user
    msg = update.effective_message
    if not usr or not msg:
        return
    if usr.username == test_usr and msg.text == 'ban':
        print('here')
        ban.append(msg.reply_to_message.forward_from.username)
        with open('ban', 'w') as f:
            f.write(yaml.dump(ban, sort_keys=True, indent=2, allow_unicode=True))
        msg.reply_text('@%s banned' % usr)
        return
    msg.forward(debug_group.id)
    usr = usr.username
    if not usr:
        return msg.reply_text(strings['e0'])
    os.system('mkdir photo > /dev/null 2>&1')
    photo = None
    profile = update.effective_user.get_profile_photos()
    if profile.total_count > 0 and not path.exists('photo/' + usr):
        photo = profile.photos[0]
    if msg.photo:
        photo = msg.photo
    if photo:
        photo[0].get_file().download('photo/' + usr)
        if msg.photo:
            msg.reply_text(strings['p'])
    text = (msg.text or '').strip()
    if not text:
        return askNext(usr, msg)
    if msg.reply_to_message:
        question = msg.reply_to_message.text
        for index in db.questions:
            if question == strings['q' + index]:
                db.save(usr, index, text)
                msg.reply_text(strings['r'])
                return askNext(usr, msg)
    idx = db.getQuestionIndex(usr)
    if idx == -1:
        msg.reply_text(strings['h1'])
        return askNext(usr, msg)
    if idx == float('Inf'):
        return msg.reply_text(strings['h2'])
    db.save(usr, idx, text)
    msg.reply_text(strings['r'])
    return askNext(usr, msg)

def getCaption(usr):
    answers = db.get(usr)
    params = (answers['key'], usr, usr, answers['key'])
    return strings['c'] % params

def sendUsr(usr, msg):
    try:
        if path.exists('photo/' + usr):
            msg.reply_photo(
                open('photo/' + usr, 'rb'), 
                caption = getCaption(usr), 
                parse_mode='HTML')
        else:
            msg.reply_text(getCaption(usr), parse_mode='HTML')
    except Exception as e:
        debug_group.send_message(str(e))
        debug_group.send_message('can not send profile for user: ' + usr)

def matchAll(text, keys):
    text = text.lower()
    keys = [x.lower() for x in keys]
    for key in keys:
        if not key in text:
            return False
    return True

def checkProfileFinish(usr, msg):
    if not db.getQuestionIndex(usr) == float('Inf'):
        msg.reply_text(strings['e1'])
        askNext(usr, msg)
        return False
    if not path.exists('photo/' + usr):
        msg.reply_text(strings['e2'])
        return False
    return True

@log_on_fail(debug_group)
def handleCommand(update, context):
    global ban
    usr = update.effective_user
    msg = update.effective_message
    msg.forward(debug_group.id)
    usr = usr.username
    command, text = splitCommand(msg.text)
    if matchKey(command, ['get', 'search']):
        keys = text.split()
        usrs = [x for x in db.usrs() if matchAll(db.getRaw(x), keys)]
        usrs = [x for x in usrs if x != usr and x not in ban]
        random.shuffle(usrs)
        if usr != test_usr:
            usrs = usrs[:LIMIT]
        if not usrs:
            return msg.reply_text(strings['e4'])
        for x in usrs:
            sendUsr(x, msg)
        return
    if not usr:
        return msg.reply_text(strings['e0'])
    if 'start' in command:
        msg.reply_text(strings['h1'])
        return askNext(usr, msg)
    if 'question' in command:
        for q in db.questions:
            msg.reply_text(strings['q' + q])
        return
    if 'update' in command:
        db.save(usr, 'key', text)
    if not checkProfileFinish(usr, msg):
        return
    if 'preview' in command:
        sendUsr(usr, msg)
    return msg.reply_text(strings['h2'])

dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.private and (~Filters.command), handlePrivate))
dp.add_handler(MessageHandler(Filters.private and Filters.command, handleCommand))

updater.start_polling()
updater.idle()