import postgresql
from datetime import datetime, timedelta

class Queue:
	"""Класс очереди. Если id пользователей изначально неизвестны, они выставляются в значение -1"""

	def __init__ (self, id, name, active, current_user_id, last_user_id):
		self.id = id
		self.name = name
		self.active = active
		self.current_user_id = current_user_id
		self.last_user_id = last_user_id

	def __str__ (self):
		return ("Queue:\nId: " + str(self.id) + "\nName: " + str(self.name) +
					"\nActive: " + str(self.active) + "\nCurrent user id: " +
					str(self.current_user_id) + "\nLast user id: " + str(self.last_user_id))


class QueueUser:
	"""Класс участника очереди. Если id других пользователей или очереди изначально неизвестны, они выставляются в значение -1"""

	def __init__(self, user_id, chat_id, queue_id, num, is_in_queue, is_in_session,
				next_user_id, prev_user_id, start_time, finish_time, session_time):

		self.id = user_id
		self.chat_id = chat_id
		self.queue_id = queue_id
		self.num = num
		self.is_in_queue = is_in_queue
		self.is_in_session = is_in_session
		self.next_user_id = next_user_id
		self.prev_user_id = prev_user_id
		self.start_time = start_time
		self.finish_time = finish_time
		self.session_time = session_time

	def __str__(self):
		return ("\nQueueUser:\nId:\t\t" + str(self.id) + "\nChat id:\t" + str(self.chat_id) +
				"\nQueue id:\t" + str(self.queue_id) + "\nNum:\t\t" + str(self.num) +
				"\nIs in queue:\t" + str(self.is_in_queue) + "\nIs in session:\t" + str(self.is_in_session) +
				"\nNext user id:\t" + str(self.next_user_id) + "\nPrev user id:\t" + str(self.prev_user_id) +
				"\nStart time:\t" + str(self.start_time) + "\nFinish time:\t" + str(self.finish_time) +
				"\nSession time:\t" + str(self.session_time))


class DataBaseExecuter:

	def __init__ (self, db_host):
		self.db = postgresql.open(db_host)

	def __enter__ (self):
		return self

	def __exit__ (self, Type, Value, Trace):
		self.db.close()


	# Работа с классом Queue

	def find_free_queue_name(self):
		"""Нахождение первого свободного имени для очереди"""
		i = 0

		check = self.db.prepare("select * from queue where active = True and name = $1")

		while len(check(str(i))) > 0:
			i = i + 1

		return str(i)


	def create_new_queue(self, name, creator_user_id):
		"""Записывает в бд новую очередь и возвращает ее"""

		queue_id = self.db.query("insert into queue (name, active, current_user_id, last_user_id) values ({}, True, {}, {}) returning id".format(
				name, creator_user_id, creator_user_id))[0][0]

		return Queue(queue_id, name, True, creator_user_id, creator_user_id)


	def find_active_queue_by_name(self, name):
		"""Находит очередь по name и возвращает ее"""

		result = self.db.query("select * from queue where active = True and name = '{}' ".format(name))

		if len(result) == 0:
			return None

		result = result[0]

		return Queue(result[0], result[1], result[2], result[3], result[4])


	def find_queue(self, queue_id):
		"""Находит очередь по queue_id и возвращает ее"""

		result = self.db.query("select * from queue where id = '{}' ".format(queue_id))

		if len(result) == 0:
			return None

		result = result[0]

		return Queue(result[0], result[1], result[2], result[3], result[4])

	
	def update_queue(self, queue):
		"""Обновляет состояние очереди, находя ее по id"""

		self.db.execute("update queue set (active, current_user_id, last_user_id) = ({},{},{}) where id = {}".format(
				queue.active, queue.current_user_id, queue.last_user_id, queue.id))



	# =================================================================================================================
	# Работа с классом QueueUser

	def create_new_user(self, chat_id, queue_id):
		"""Записывает в бд нового пользователя и возвращает его"""

		user_id = self.db.query("insert into queue_user (chat_id, queue_id) values ({}, {}) returning id".format(chat_id, queue_id))[0][0]

		return QueueUser(user_id, chat_id, queue_id, 0, True, False, -1, -1, datetime.now(), datetime.now(), timedelta())


	def find_user(self, user_id):
		"""Находит пользователя по user_id и возвращает его"""

		result = self.db.query("select * from queue_user where id = {}".format(user_id))

		if len(result) == 0:
			return None

		result = result[0]

		return QueueUser(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10])


	def find_user_in_queue_by_chat_id(self, chat_id):
		"""Находит пользователя с is_in_queue = True по chat_id и возвращает его"""

		result = self.db.query("select * from queue_user where chat_id = {} and is_in_queue = True".format(chat_id))

		if len(result) == 0:
			return None

		result = result[0]

		return QueueUser(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10])


	def update_user(self, user):
		"""Обновляет состояние queue_user, находя его по id"""

		self.db.execute("update queue_user set (queue_id, num, is_in_queue, is_in_session, next_user_id, prev_user_id, start_time, finish_time, session_time)" +
				" = ({}, {}, {}, {}, {}, {}, '{}', '{}', '{}') where id = {}".format(
				user.queue_id, user.num, user.is_in_queue, user.is_in_session, user.next_user_id, user.prev_user_id, user.start_time, user.finish_time, user.session_time, user.id))


	def user_is_in_queue(self, chat_id):
		"""Проверяет, существует ли стоящий в очереди пользователь с данным chat_id"""

		find_user_in_queue = self.db.query("select * from queue_user where is_in_queue = true and chat_id = {}".format(chat_id))

		return len(find_user_in_queue) > 0

	def find_all_ex_users_in_queue(self, queue_id):

		user_ids = self.db.query("select id from queue_user where queue_id = {} and is_in_queue = false and is_in_session = false".format(queue_id))

		users = []

		print(user_ids)

		for user_id in user_ids:
			users.append(self.find_user(user_id[0]))

		return users











