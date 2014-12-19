#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import sys
import time
from optparse import OptionParser
import formatter

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#tildetown',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='quote_bot',
                  help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()

def ping():
  ircsock.send("PONG :pingis\n")  

def sendmsg(chan , msg):
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n") 

def joinchan(chan):
  ircsock.send("JOIN "+ chan +"\n")

def hello():
  ircsock.send("PRIVMSG "+ channel +" :Hello!\n")

def random_quote(channel):
  quote = os.popen("/home/frs/quotes/randquote.py").read()
  if len(quote) >= 256:
    quote = quote[:253] + '...'
  ircsock.send("PRIVMSG "+ channel +" :" + quote + "\n")

def haiku(channel):
  h = os.popen("haiku").read().replace("\n", " // ")
  ircsock.send("PRIVMSG "+ channel +" :" + h + "\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def get_user_from_message(msg):
  try:
    i1 = msg.index(':') + 1
    i2 = msg.index('!')
    return msg[i1:i2]
  except ValueError:
    return ""

# Returns the text after the bot command
def get_text_from_formatted(fmt):
  try:
    command_text = fmt.split('\t', 2)[2:][0]
    text = command_text.split(' ', 1)[1:]
    if len(text) > 0:
      return text[0].replace("\"", "\\\"")
    else:
      return ""
  except ValueError:
    return ""

def say_mentions(user, message):
  nick = get_user_from_message(message)
  menschns = os.popen("/home/karlen/bin/mensch -u %s -t 24 -z +0" % (user)).read().replace("\t", ": ").split("\n")
  for mention in menschns:
    if not "" == mention:
      toSend = "PRIVMSG "+ nick + " :" + mention + "\n"
      if len(toSend) >= 256:
        toSend = toSend[:253] + '...'
      ircsock.send(toSend)

def say_chatty(channel):
  chattyOut = os.popen("/home/karlen/bin/chatty").read().split("\n")
  for line in chattyOut:
    if line:
      ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def do_tweet(channel, fmt):
  text = get_text_from_formatted(fmt)
  chars = len(text)
  if chars > 140:
    ircsock.send("PRIVMSG "+ channel + " :Text has " + str(chars) + " chars, but it must have < 140 to tweet.\n")
  elif chars < 1:
    ircsock.send("PRIVMSG "+ channel +" :I won't tweet nothing.\n")
  else:
    os.popen("echo \"%s\" | tweet > /dev/null" % text)
        
    

def listen():
  while 1:

    time.sleep(1)

    ircmsg = ircsock.recv(2048)
    ircmsg = ircmsg.strip('\n\r')

    if ircmsg.find("PING :") != -1:
      ping()
    
    formatted = formatter.format_message(ircmsg)

    if "" == formatted:
      continue
    
    print formatted

    split = formatted.split("\t")
    timestamp = split[0]
    user = split[1]
    messageText = split[2]

    if ircmsg.find(":!quote") != -1:
      random_quote(options.channel)

    if ircmsg.find(":!mentions") != -1:
      say_mentions(user, ircmsg)

    if ircmsg.find(":!chatty") != -1:
      say_chatty(options.channel)

    if ircmsg.find(":!haiku") != -1:
      haiku(options.channel)

    if ircmsg.find(":!tweet") != -1:
      do_tweet(options.channel, formatted)

    if ircmsg.find("PING :") != -1:
      ping()

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()




