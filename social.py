#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import time
import os
import traceback as tb
from telegram_util import log_on_fail, getTmpFile, autoDestroy, matchKey
import yaml

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

updater = Updater(credential['token'], use_context=True)
tele = updater.bot
debug_group = tele.get_chat(-1001198682178)

@log_on_fail(debug_group)
def handlePrivate(update, context):
	msg = update.effective_message
	if not update.effective_message:
		return

dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.private, handlePrivate))

updater.start_polling()
updater.idle()