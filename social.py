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

HELP = 'Welcome to social bot. We help people meet each other and make friends.'
HELP2 = '''You have filled our questionare. Here are some command you may use:
/preview: preview your profile
/get: get up to 10 potential matches 
/get keyword: get up to 10 potential matches with keyword
/questions: get the question list

Reply any question to update your questionare. 
Upload any photo will overwrite your social profile photo.'''
HELP_AFTER_PREVIEW = '''/questions: get the question list

Reply any question to update your questionare. 
Upload any photo will overwrite your social profile photo.'''
CAPTION = '''Here for: %s
Age: %s
Location: %s
Language(s): %s
Keywords: ***%s***
In the past 5 years: %s
Contact: t.me/%s'''

test_usr = 'b4cxb'
test_usr_id = 420074357
db = DB()

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

with open('questions') as f:
    questions = yaml.load(f, Loader=yaml.FullLoader)

updater = Updater(credential['token'], use_context=True)
tele = updater.bot
debug_group = tele.get_chat(-1001198682178)

def askNext(usr, msg):
    idx = db.getQuestionIndex(usr, ask=True)
    if idx == len(questions):
        return msg.reply_text(HELP2)
    msg.reply_text(questions[idx])

@log_on_fail(debug_group)
def handlePrivate(update, context):
    usr = update.effective_user
    msg = update.effective_message
    if not usr or not msg:
        return
    usr = usr.username
    if not usr:
        return msg.reply_text('Please Specify username before using me.')
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
            msg.reply_text('Received/updated your photo.')
    text = (msg.text or '').strip()
    if not text:
        return askNext(usr, msg)
    if msg.reply_to_message:
        question = msg.reply_to_message.text
        if question in questions:
            index = questions.index(question)
            db.save(usr, index, text)
            msg.reply_text('Your answer recorded.')
            return askNext(usr, msg)
    idx = db.getQuestionIndex(usr)
    if idx == None:
        msg.reply_text(HELP)
        return askNext(usr, msg)
    if idx == len(questions):
        return msg.reply_text(HELP2)
    db.save(usr, idx, text)
    msg.reply_text('Your answer recorded.')
    return askNext(usr, msg)

def getCaption(usr):
    params = tuple([db.get(usr).get(x) for x in range(len(questions))] + [usr])
    return CAPTION % params

def sendUsr(usr, msg):
    msg.reply_photo(
        open('photo/' + usr, 'rb'), 
        caption = getCaption(usr), 
        parse_mode='Markdown')

@log_on_fail(debug_group)
def handleCommand(update, context):
    usr = update.effective_user
    msg = update.effective_message
    usr = usr.username
    if not usr:
        return msg.reply_text('Please specify username before using me.')
    command, text = splitCommand(msg.text)
    if 'preview' in command:
        if not path.exists('photo/' + usr):
            return msg.reply_text('Please upload your photo.')
        if not db.getQuestionIndex(usr) == len(questions):
            msg.reply_text('Please finish your questionare.')
            return askNext(usr, msg)
        sendUsr(usr, msg)
        return msg.reply_text(HELP_AFTER_PREVIEW)
    if 'get' in command:
        keys = text.split()
        print(db.usrs())
        usrs = [x for x in db.usrs() if matchKey(db.getRaw(x), keys)]
        print(usrs)
        usrs = [x for x in usrs if x != usr]
        random.shuffle(usrs)
        if usr != test_usr:
            usrs = usrs[:LIMIT]
        if not usrs:
            return msg.reply_text('No match user, please try again later.')
        for x in usrs:
            sendUsr(usr, msg)
        return
    if 'start' in command:
        msg.reply_text(HELP)
        return askNext(usr, msg)



dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.private and (~Filters.command), handlePrivate))
dp.add_handler(MessageHandler(Filters.private and Filters.command, handleCommand))

updater.start_polling()
updater.idle()