#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import log_on_fail, splitCommand, matchKey
import yaml
import os
from os import path
from db import DB
import random

LIMIT = 10

test_usr = 'b4cxb'
db = DB()

if 'chinese' in str(sys.argv):
    lan = 'zh'
else:
    lan = 'en'

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

with open(lan + '_string') as f:
    strings = yaml.load(f, Loader=yaml.FullLoader)

updater = Updater(credential[lan + '_token'], use_context=True)
tele = updater.bot
debug_group = tele.get_chat(-1001198682178)

def askNext(usr, msg):
    idx = db.getQuestionIndex(usr, ask=True)
    if idx == db.NUM_Q:
        return msg.reply_text(strings['h2'])
    msg.reply_text(questions[idx])

@log_on_fail(debug_group)
def handlePrivate(update, context):
    usr = update.effective_user
    msg = update.effective_message
    if not usr or not msg:
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
        if question in questions:
            index = questions.index(question)
            db.save(usr, index, text)
            msg.reply_text(strings['r'])
            return askNext(usr, msg)
    idx = db.getQuestionIndex(usr)
    if idx == None:
        msg.reply_text(strings['h1'])
        return askNext(usr, msg)
    if idx == db.NUM_Q:
        return msg.reply_text(strings['h2'])
    db.save(usr, idx, text)
    msg.reply_text(strings['r'])
    return askNext(usr, msg)

def getCaption(usr):
    answers = [db.get(usr).get(x) for x in range(db.NUM_Q)]
    params = tuple(answers + [usr, usr, answers[4]])
    return strings['c'] % params

def sendUsr(usr, msg):
    try:
        msg.reply_photo(
            open('photo/' + usr, 'rb'), 
            caption = getCaption(usr), 
            parse_mode='HTML')
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
    if not db.getQuestionIndex(usr) == db.NUM_Q:
        msg.reply_text(strings['e1'])
        askNext(usr, msg)
        return False
    if not path.exists('photo/' + usr):
        msg.reply_text(strings['e2'])
        return False
    return True

@log_on_fail(debug_group)
def handleCommand(update, context):
    usr = update.effective_user
    msg = update.effective_message
    msg.forward(debug_group.id)
    usr = usr.username
    command, text = splitCommand(msg.text)
    if matchKey(command, 'get', 'search'):
        keys = text.split()
        usrs = [x for x in db.usrs() if matchAll(db.getRaw(x), keys)]
        usrs = [x for x in usrs if x != usr]
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
        for q in questions:
            msg.reply_text(q)
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