import config
import telebot
from data_base_executer import DataBaseExecuter

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start_queue'])
def start_queue(message):

	db = DataBaseExecuter()
	bot.send_message(message.chat.id, "You've started queue with number " + str(db.start_new_queue()))


@bot.message_handler(commands=['join_queue'])
def join_queue(message):

	db = DataBaseExecuter()
	queue_name = message.text.split(" ")[1]

	result = db.join_queue(message.chat.id, queue_name)

	if result == -1:
		bot.send_message(message.chat.id, "There is no such queue :(")
	elif result == -2:
		bot.send_message(message.chat.id, "You are already in a queue")
	else:
		bot.send_message(message.chat.id, "You have successfully joined to queue " + queue_name + " with number " + str(result))


@bot.message_handler(commands=['finish'])
def finish_queue(message):
	
	db = DataBaseExecuter()

	result = db.finish_queue(message.chat.id)

	if result == -1:
		bot.send_message(message.chat.id, "It seems, that you are not in any queue")
	else:
		bot.send_message(message.chat.id, "Good luck!")

		if result != -2:
			bot.send_message(result, "It's your time!")
	
	
	

if __name__ == '__main__':
	bot.polling(none_stop=True)
