
# Start Queue responds
def queue_started_respond (queue_name):
	return "You've started queue with number " + queue_name


# Join Queue responds
queue_start_bad_format_respond = "Bad format"

no_such_queue_respond = "There is no such queue :("

already_in_queue_respond = "You are already in a queue"

def join_success_respond (queue_name, number):
	return "You have successfully joined to queue " + queue_name + " with number " + number


# Finish Queue responds
not_in_queue_respond = "It seems, that you are not in any queue"

call = "It's your time"

goodbye_respond = "Good luck!"