#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import log_on_fail, splitCommand
import yaml
import os
from os import path
from db import DB

HELP = 'Welcome to social bot. We help people meet each other and make friends.'
HELP2 = '''You have filled our questionare. Here are some command you may use:
/preview: preview your profile
/get: get a potential match
/questions: get the question list

Reply any question to update your profile. 
Upload any photo will overwrite your social profile photo.
'''

db = DB()

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

with open('questions') as f:
    questions = yaml.load(f, Loader=yaml.FullLoader)

updater = Updater(credential['token'], use_context=True)
tele = updater.bot
debug_group = tele.get_chat(-1001198682178)

def askNext(usr, msg):
	idx = db.getQuestionIndex(usr)
	if idx == len(questions):
		return
	msg.reply(questions[idx])

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
	if profile.total_count > 0 and 
		not path.exists('photo/' + usr):
		photo = profile.photos[0]
	if msg.photo:
		photo = msg.photo
	if photo:
		photo[0].get_file().download('photo/' + usr)
		msg.reply_text('Received/updated your photo.')
		return askNext(usr, msg)
	text = msg.text
	if not text:
		return
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
	db.save(user, idx, text)
	msg.reply_text('Your answer recorded.')
	return askNext(usr, msg)


dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.private and (~Filters.command), handlePrivate))
dp.add_handler(MessageHandler(Filters.private and Filters.command, handleCommand))

updater.start_polling()
updater.idle()