import config
import telebot
import dialogs

from data_base_executer import DataBaseExecuter, Queue, QueueUser
from datetime import datetime, timedelta

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start_queue'])
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

		bot.send_message(message.chat.id, dialogs.queue_started_respond(str(queue.name)))


@bot.message_handler(commands=['join_queue'])
def join_queue(message):

	if (len(message.text.split(" ")) != 2):
		bot.send_message(message.chat.id, dialogs.queue_start_bad_format_respond)
		return

	with DataBaseExecuter(config.db_host) as db:

		if (db.user_is_in_queue(message.chat.id)):
			bot.send_message(message.chat.id, dialogs.already_in_queue_respond)
			return

		queue_name = message.text.split(" ")[1]

		queue = db.find_active_queue_by_name(queue_name)

		if queue == None:
			bot.send_message(message.chat.id, dialogs.no_such_queue_respond)
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

		bot.send_message(message.chat.id, dialogs.join_success_respond(queue.name, str(new_user.num)))


@bot.message_handler(commands=['finish'])
def finish_queue(message):
	
	with DataBaseExecuter(config.db_host) as db:

		user = db.find_user_in_queue_by_chat_id(message.chat.id)

		if user == None:
			bot.send_message(message.chat.id, dialogs.not_in_queue_respond)
			return

		queue = db.find_queue(user.queue_id)

		if queue.current_user_id != user.id:
			bot.send_message(message.chat.id, dialogs.not_your_turn_respond)
			return

		if user.id == queue.last_user_id:
			queue.active = False
		else:
			next_user = db.find_user(user.next_user_id)
			next_user.is_in_session = True
			next_user.start_time = datetime.now()

			queue.current_user_id = next_user.id

			db.update_user(next_user)
			bot.send_message(next_user.chat_id, dialogs.call)

		user.is_in_queue = False
		user.is_in_session = False

		user.finish_time = datetime.now()
		user.session_time = user.finish_time - user.start_time

		db.update_user(user)
		db.update_queue(queue)
		bot.send_message(message.chat.id, dialogs.goodbye_respond)
		

if __name__ == '__main__':
	bot.polling(none_stop=True)
