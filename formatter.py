import time
import re

def format_message(message):
	pattern = r'^:.*\!~(.*)@.* PRIVMSG #tildetown :(.*)'
	now = int(time.time())
	matches = re.match(pattern, message)
	if not matches:
		return ''

	message = matches.group(2).strip()
	nick    = matches.group(1).strip()

	return "%s\t%s\t%s" % (now, nick, message)