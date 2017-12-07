import postgresql
import config

class DataBaseExecuter:

	def __init__ (self):
		self.db = postgresql.open(config.db_host)


	def start_new_queue(self):
		""" Cоздание новой очереди """

		i = 0
		with self.db as db:

			# Нахождение первого свободного названия из ряда 1, 2, 3 ...
			check = db.prepare("select * from queue where queue.active = True and queue.name = $1")
			while len(check(str(i))) > 0:
				i = i + 1

			# Создание очереди 
			create = db.prepare("insert into queue (name, active) values ($1, True)")
			create(str(i))

		return i


	def join_queue(self, chat_id ,queue_name):
		""" Присоединение к новой очереди """

		with self.db as db:

			# Проверяем, не стоит ли пользователь уже в какой-нибудь очерди
			find_queue_user = db.prepare("select * from queue_user where waiting = true and chat_id = $1")
			if find_queue_user(chat_id):
				return -2;

			# Находим очередь по имени
			find_queue = db.prepare("select id from queue where queue.active = True and queue.name = $1")
			queue_result = find_queue(queue_name)

			# Если очередь не существует или не активна, возвращаем -1
			if len(queue_result) == 0:
				return -1

			# Получаем id нужной очереди
			queue_id = queue_result[0][0]

			# Находим номер последнего пользователя, ставшего в очередь
			find_last_user_num = db.prepare("select num from queue_user where num = (select max(num) from queue_user where queue_id = $1) and queue_id = $1")
			last_user_num_result = find_last_user_num(queue_id)

			# Если пользователей в очереди нет, то присвавыем нововому пользователю номер 0, иначе на один больше от последнего пользователя в очереди
			user_num = 0
			if len(last_user_num_result) > 0:
				user_num = find_last_user_num(queue_id)[0][0] + 1

			# Если очередь найдена, вставляем пользователя в базу данных
			paste_user = db.prepare("insert into queue_user (queue_id, chat_id, num, waiting) values ($1, $2, $3, True)")
			paste_user(queue_id, chat_id, user_num)

			# Возвращаем 0 в случае успешного добавления пользователя
			return user_num


	def finish_queue(self, chat_id):
		""" Окончание стояния в очереди """

		with self.db as db:

			# Находим очередь и номер пользователя по chat_id
			find_queue_user = db.prepare("select (queue_id, num) from queue_user where queue_user.waiting = True and queue_user.chat_id = $1")
			queue_user_result = find_queue_user(chat_id)

			# Если такого пользователя не существует возвращаем -1
			if len(queue_user_result) == 0:
				return -1

			# Переключаем статус пользователя на waiting = false
			change_user_status = db.prepare("update queue_user set waiting = false where waiting = true and chat_id = $1")
			change_user_status(chat_id)

			# Получаем id нужной очереди
			queue_id = queue_user_result[0][0][0]

			# Получаем номер пользователя в очереди
			queue_user_num = queue_user_result[0][0][1]

			# Находим следующего пользоватлея в этой очереди
			find_next_queue_user = db.prepare("select chat_id from queue_user where queue_user.waiting = True and queue_user.queue_id = $1 and queue_user.num = $2")
			next_queue_user_result = find_next_queue_user(queue_id, queue_user_num + 1)

			# Если такого пользователя не существует переключаем статус очереди на active = false и возвращаем -2
			if len(next_queue_user_result) == 0:
				find_queue = db.prepare("update queue set active = false where id = $1")
				find_queue(queue_id)
				return -2

			# Получаем chat_id нужного пользователя и возвращаем его
			next_queue_user_chat_id = next_queue_user_result[0][0]
			return next_queue_user_chat_id











