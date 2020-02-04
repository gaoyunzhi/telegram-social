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
Keywords: <b>%s</b>
In the past 5 years: %s
Contact: t.me/%s
Contect Template: Hey, I have seen you by @friends_social_bot, I'm also very interested in %s. May we be friends?'''

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
    answers = [db.get(usr).get(x) for x in range(len(questions))]
    params = tuple(answers + [usr, answers[4]])
    return CAPTION % params

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
    if not db.getQuestionIndex(usr) == len(questions):
        msg.reply_text('Please finish your questionare first.')
        askNext(usr, msg)
        return False
    if not path.exists('photo/' + usr):
        msg.reply_text('Please upload your photo first.')
        return False
    return True

@log_on_fail(debug_group)
def handleCommand(update, context):
    usr = update.effective_user
    msg = update.effective_message
    usr = usr.username
    if not usr:
        return msg.reply_text('Please specify username before using me.')
    command, text = splitCommand(msg.text)
    if 'start' in command:
        msg.reply_text(HELP)
        return askNext(usr, msg)
    if 'questions' in command:
        for q in questions:
            msg.reply_text(q)
        return
    if not checkProfileFinish(usr, msg):
        return
    if 'preview' in command:
        sendUsr(usr, msg)
        return msg.reply_text(HELP_AFTER_PREVIEW)
    if 'get' in command:
        keys = text.split()
        usrs = [x for x in db.usrs() if matchAll(db.getRaw(x), keys)]
        usrs = [x for x in usrs if x != usr]
        random.shuffle(usrs)
        if usr != test_usr:
            usrs = usrs[:LIMIT]
        if not usrs:
            return msg.reply_text('No match user, please try again later.')
        for x in usrs:
            sendUsr(x, msg)
        return
    return msg.reply_text(HELP2)

dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.private and (~Filters.command), handlePrivate))
dp.add_handler(MessageHandler(Filters.private and Filters.command, handleCommand))

updater.start_polling()
updater.idle()