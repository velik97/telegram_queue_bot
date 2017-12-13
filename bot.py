import config
import telebot
import dialogs
from data_base_executer import DataBaseExecuter

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start_queue'])
def start_queue(message):

	db = DataBaseExecuter(config.db_host)
	bot.send_message(message.chat.id, dialogs.queue_started_respond(str(db.start_new_queue())))


@bot.message_handler(commands=['join_queue'])
def join_queue(message):

	db = DataBaseExecuter(config.db_host)

	if (len(message.text.split(" ")) != 2):
		bot.send_message(message.chat.id, dialogs.queue_start_bad_format_respond)
		return

	queue_name = message.text.split(" ")[1]

	result = db.join_queue(message.chat.id, queue_name)

	if result == -1:
		bot.send_message(message.chat.id, dialogs.no_such_queue_respond)
	elif result == -2:
		bot.send_message(message.chat.id, dialogs.already_in_queue_respond)
	else:
		bot.send_message(message.chat.id, dialogs.join_success_respond(queue_name, str(result)))


@bot.message_handler(commands=['finish'])
def finish_queue(message):
	
	db = DataBaseExecuter(config.db_host)

	result = db.finish_queue(message.chat.id)

	if result == -1:
		bot.send_message(message.chat.id, dialogs.not_in_queue_respond)
	else:
		bot.send_message(message.chat.id, dialogs.goodbye_respond)

		if result != -2:
			bot.send_message(result, dialogs.call)
	
	
	

if __name__ == '__main__':
	bot.polling(none_stop=True)
