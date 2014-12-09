def find_mentions(msg):
	user     = get_user_from_message(msg)
	messages = []
	with open("log", "r") as f:
		for line in f:
			message = line.strip('\n\r').split(':')[-1]
			if message.find(user) != -1:
				sender = get_user_from_message(line)
				if sender != "":
					messages.append(sender + ': ' + message)
	return (user, messages)

def get_user_from_message(msg):
	try:
		i1 = msg.index(':') + 1
		i2 = msg.index('!')
		return msg[i1:i2]
	except ValueError:
		return ""