#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
from datetime import datetime
from datetime import timedelta
import time


updater = None
belgapino = [TELEGRAM_ID]

# Mensajes
mensajes_enviados = dict()


for persona in belgapino:
	mensajes_enviados[persona] = []
	
	
	
# Setup loggin config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading bot...")
logger.info("I've readed these models: ")


def cuantoQueda():

	now = datetime.now()

	hora_ahora = datetime(now.year, now.month, now.day, now.hour, 0, 0)

	la_hora_que_viene = hora_ahora + timedelta(hours=1)

	minutos_actuales = now - hora_ahora

	alerta_en = [(la_hora_que_viene-minutos_actuales).minute,(la_hora_que_viene-minutos_actuales).second]

	envia_mensaje("Empiezo a avisar en " + str(alerta_en[0]) + " minutos " + str(alerta_en[1]) + " segundos")

	return (alerta_en[0]*60)+alerta_en[1]




def registra_mensaje_enviado(persona,message_id):
	global mensajes_enviados
	mensajes_enviados[persona].append(message_id) 

def envia_mensaje(text):
	global updater
	global belgapino
	global mensajes_enviados
	for chat in belgapino:
		mensaje_enviado = updater.bot.send_message(chat_id=chat, text =text, parse_mode="HTML")
		registra_mensaje_enviado(chat,mensaje_enviado.message_id)
		
	logger.info(text)
	
def campanadas(context):
	envia_mensaje("TOLÓN")
	
	
def borrar_mensajes_enviados(context):
	global mensajes_enviados
	global updater
	global belgapino
	
	for usuario_chat_id in belgapino:
		try:
			if mensajes_enviados[usuario_chat_id] != []:
				for mensaje in mensajes_enviados[usuario_chat_id]:
					updater.bot.edit_message_text(chat_id=usuario_chat_id, message_id = mensaje, text="Bórrame.", parse_mode="HTML")
					try:
						updater.bot.delete_message(chat_id=usuario_chat_id, message_id = mensaje)
					except:
						continue
				mensajes_enviados[usuario_chat_id] = []
		except Exception as e:
			logger.error("Al borrar mensajes anteriores he petado.")
			logger.error(str(e))
			continue
	
	
def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)
	
def add(update,context):
	global belgapino
	id = update.message.chat_id
	if id not in belgapino:
		belgapino.append(update.message.chat_id)
		updater.bot.send_message(chat_id=update.message.chat_id, text="Bienvenido")
	
def init(update,context):

	logger.debug("Recibo señal de INIT de %s", update.message.chat_id)
	if not validaUsuario(update.message.chat_id):
		return
	#limpiarTodo("Limpio porque se ha hecho init")
	

	#campanadas(update)	
	try:
		context.job_queue.run_repeating(campanadas,3600,first=cuantoQueda(),context= update)
		context.job_queue.run_repeating(borrar_mensajes_enviados,3600,first=cuantoQueda()+60,context= update)
	except Exception as e:
		logger.error("Ha fallado el trabajo repetitivo: " + + str(e))
		#envia_mensaje("Fallo al hacer init porque " + str(e))
	return


def validaUsuario(usuario):
	global belgapino
	if usuario in belgapino:
		return True
	else:
		responder(usuario,"You have nothing to do here.")
		envia_mensaje("Un extraño ha intentado usar el bot!: " + usuario)
		return False


def main():
	import telekey
	global updater
		
	if updater is not None:
		updater.stop()

	logger.info("Inicializando bot.")
	updater = Updater(telekey.telekey, use_context=True)
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	#dp.add_handler(CommandHandler("start", start, pass_job_queue=True))
	dp.add_handler(CommandHandler("init", init, pass_job_queue=True))
	#dp.add_handler(CommandHandler("stop", stop, pass_job_queue=True))
	dp.add_handler(CommandHandler("add", add))
	#dp.add_handler(CommandHandler("quit", quit, pass_job_queue=True))
	
	# on noncommand i.e message - echo the message on Telegram
	#dp.add_handler(MessageHandler(Filters.text, echo))
	#dp.add_handler(MessageHandler(Filters.document, descargaWanted))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	logger.info("Bot listo.")
	
	#envia_mensaje("El bot se ha reiniciado, que alguien haga /init.")
	
	updater.idle()


if __name__ == '__main__':
	main()
