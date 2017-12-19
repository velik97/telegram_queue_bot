import telebot
import cherrypy

import config
import dialogs
import utils

from data_base_executer import DataBaseExecuter, Queue, QueueUser
from datetime import datetime, timedelta

WEBHOOK_HOST = '78.155.206.129'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

@bot.message_handler(commands=['start'])
def start(message):

	bot.send_message(message.chat.id, 'Приветик', reply_markup=utils.not_in_queue_markup())

@bot.message_handler(regexp=['Начать очередь'])
def start_queue(message):

	with DataBaseExecuter(config.db_host) as db:

		if (db.user_is_in_queue(message.chat.id)):
			bot.send_message(message.chat.id, dialogs.already_in_queue_respond)
			return

		creator = db.create_new_user(message.chat.id, -1)
		queue = db.create_new_queue(db.find_free_queue_name(), creator.id)

		creator.queue_id = queue.id
		creator.is_in_session = True

		db.update_user(creator)

		bot.send_message(message.chat.id, dialogs.queue_started_respond(str(queue.name)), reply_markup = utils.finish_queue_markup())
		return


@bot.message_handler(regexp=['Присоединиться к очереди'])
def pre_join_queue(message):

	with DataBaseExecuter(config.db_host) as db:

        if (db.user_is_in_queue(message.chat.id)):
            bot.send_message(message.chat.id, dialogs.already_in_queue_respond)
            return

		msg = bot.send_message(message.chat.id, 'Укажите номер очереди', reply_markup = utils.chose_queue_name_markup())

		bot.register_next_step_handler(msg, join_queue)


def join_queue(message):

	with DataBaseExecuter(config.db_host) as db:

		queue_name = message.text

		queue = db.find_active_queue_by_name(queue_name)

		if queue == None:
			msg = bot.send_message(message.chat.id, dialogs.no_such_queue_respond)
			bot.register_next_step_handler(msg, join_queue)
			return

		new_user = db.create_new_user(message.chat.id, queue.id)
		last_user = db.find_user(queue.last_user_id)

		new_user.prev_user_id = last_user.id
		new_user.num = last_user.num + 1

		last_user.next_user_id = new_user.id

		queue.last_user_id = new_user.id

		db.update_user(last_user)
		db.update_user(new_user)
		db.update_queue(queue)

		bot.send_message(message.chat.id, dialogs.join_success_respond(queue.name, str(new_user.num)), reply_markup = utils.clear_prev_markup())


@bot.message_handler(regexp=['Закончить'])
def finish_queue(message):
	
	with DataBaseExecuter(config.db_host) as db:

		user = db.find_user_in_queue_by_chat_id(message.chat.id)

		if user == None:
			bot.send_message(message.chat.id, dialogs.not_in_queue_respond)
			return

		queue = db.find_queue(user.queue_id)

		if queue.current_user_id != user.id:
			msg = bot.send_message(message.chat.id, dialogs.not_your_turn_respond)
			return

		if user.id == queue.last_user_id:
			queue.active = False
		else:
			next_user = db.find_user(user.next_user_id)
			next_user.is_in_session = True
			next_user.start_time = datetime.now()

			queue.current_user_id = next_user.id

			db.update_user(next_user)
			bot.send_message(next_user.chat_id, dialogs.call, reply_markup = utils.finish_queue_markup())

		user.is_in_queue = False
		user.is_in_session = False

		user.finish_time = datetime.now()
		user.session_time = user.finish_time - user.start_time

		db.update_user(user)
		db.update_queue(queue)
		bot.send_message(message.chat.id, dialogs.goodbye_respond, reply_markup = utils.not_in_queue_markup())


bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
