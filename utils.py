from telebot import types

def not_in_queue_markup():
	
	markup = types.ReplyKeyboardMarkup()
	markup.row('/Начать_очередь')
	markup.row('/Присоединиться_к_очереди')

	return markup

def chose_queue_name_markup():
	
	markup = types.ReplyKeyboardMarkup()
	markup.row('1', '2', '3')
	markup.row('4','5','6')
	markup.row('7','8','9')
	markup.row('Отменить', '0')

	return markup

def finish_queue_markup():

	markup = types.ReplyKeyboardMarkup()
	markup.row('/Закончить')

	return markup

def clear_prev_markup():
	return types.ReplyKeyboardRemove()
