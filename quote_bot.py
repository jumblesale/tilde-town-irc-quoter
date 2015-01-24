#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import os.path
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

blacklist = []

# check if there's a blacklist
if os.path.isfile('./blacklist'):
  blacklist = open('./blacklist').read().split("\n")

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

def random_quote_apropos(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) > 1:
    message = "Sorry, q-apropos only accepts 1 or 0 arguments."
  else:
    if len(args) == 1:
      term = args[0]
    else:
      term = ""
    message = quote_apropos("--apropos", term)
  sendmsg(channel, message)

def random_quote_from(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    message = "Sorry, q-from only accepts 1 argument."
  else:
    if len(args) == 1:
      term = args[0]
      message = quote_apropos("--from", term)
  sendmsg(channel, message)

def haiku(channel):
  h = os.popen("haiku").read().replace("\n", " // ")
  ircsock.send("PRIVMSG "+ channel +" :" + h + "\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def say_mentions(user, message):
  nick = get_user_from_message(message)
  menschns = os.popen("/home/karlen/bin/mensch -u %s -t 24 -z +0" % (user)).read().replace("\t", ": ").split("\n")
  for mention in menschns:
    if not "" == mention:
      toSend = "PRIVMSG "+ nick + " :" + mention + "\n"
      if len(toSend) >= 256:
        toSend = toSend[:253] + '...'
      ircsock.send(toSend)

def say_catchup(user):
  catchups = os.popen("/home/karlen/bin/catchup").read().split("\n")
  for line in catchups:
    if not "" == line:
      toSend = "PRIVMSG "+ user + " :" + line + "\n"
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
    # add confimration message 
    
def list_commands(channel):
  sendmsg(channel, "Enter a command proceeded by a !: quote, q-apropos, q-from, mentions, chatty, haiku, tweet, banter, commands")
  
## FUNCTIONS FOR PARSING THE IRC MESSAGES

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


def top_bants(channel):
  text = os.popen("/home/karlen/bin/mensch -b | shuf -n 1").read().split("\t")[2]
  if text:
    ircsock.send("PRIVMSG "+ channel + " :" + text + "\n")


## INTERFACE TO quote_apropos.hs

def quote_apropos(flag, arg):
  args = flag + " " + arg
  return os.popen("/home/um/bin/quoteapropos " + args).read()
  
  

## LISTENER FUNCTION

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
    

    split = formatted.split("\t")
    timestamp = split[0]
    user = split[1]
    messageText = split[2]

    if user in blacklist:
      continue
    
    print formatted

    if ircmsg.find(":!quote") != -1:
      random_quote(options.channel)
      
    if ircmsg.find(":!q-apropos") != -1:
      random_quote_apropos(options.channel, formatted)

    if ircmsg.find(":!q-from") != -1:
      random_quote_from(options.channel, formatted)

    if ircmsg.find(":!mentions") != -1:
      say_mentions(user, ircmsg)

    if ircmsg.find(":!chatty") != -1:
      say_chatty(options.channel)

    if ircmsg.find(":!catchup") != -1:
      say_catchup(user)

    if ircmsg.find(":!haiku") != -1:
      haiku(options.channel)

    if ircmsg.find(":!tweet") != -1:
      do_tweet(options.channel, formatted)

    if ircmsg.find(":!commands") != -1:
      list_commands(options.channel)

    if ircmsg.find(":!banter") != -1:
      top_bants(options.channel)

    if ircmsg.find("PING :") != -1:
      ping()

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()




