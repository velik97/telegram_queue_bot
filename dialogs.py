
#Start
welcome = "Приветик, с помощью меня ты сможешь с кайфом организовать очередь"

# Start Queue responds
def queue_started_respond (queue_name):
	return "Я сделал для тебя очередь под номером " + queue_name "\nПозови сюда своих друзей"


# Join Queue responds
queue_start_bad_format_respond = "Что-то не так, не могу разобраться :("

no_such_queue_respond = "Такой очереди нету :("

already_in_queue_respond = "Алё-малё, ты уже в очереди!"

choise_queue_respond = "Укажи номер очереди, в которой хочешь потусить"

accept_canel = "Ну не хочешь, как хочешь"

def join_success_respond (queue_name, number):
	return "Ура! Теперь ты стоишь в очереди номер " + queue_name + "\nТвой номер в этой очереди " + number


# Finish Queue responds
not_in_queue_respond = "Такс, похоже ты еще не в очереди"

not_your_turn_respond = "Погоди, впереди еще народ!"

call = "Ура, наконец-то твой черед!"

goodbye_respond = "До встречи!\nВозвращайся как можно скорее, а то мне тут скучно..."