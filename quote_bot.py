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
  quote = os.popen("/home/karlen/irc/randquote.py").read()
  if len(quote) >= 256:
    quote = quote[:253] + '...'
  ircsock.send("PRIVMSG "+ channel +" :" + quote + "\n")

def random_quote_apropos(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    message = "Sorry, q-apropos only accepts 1 argument."
  else:
    if len(args) == 1:
      term = args[0]
    else:
      term = ""
    message = quote_apropos("--apropos", term)
    if len(message) >= 256:
        message =  message[:253] + '...'
  sendmsg(channel, message)

def random_quote_from(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    message = "Sorry, q-from only accepts 1 argument."
  else:
    if len(args) == 1:
      term = args[0]
      message = quote_apropos("--from", term)
    if len(message) >= 256:
        message =  message[:253] + '...'
  sendmsg(channel, message)

def random_thing(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    sendmsg(channel, "Sorry, !random only works with: !random youtube, !random image, !random link, !random gif, !random tilde.")
  else:
    type = args[0]
    if type == "image":
        rantin = os.popen("/home/karlen/bin/mensch -i | shuf -n 1 | awk -F '\t' '{print $3}'").read().split("\n")
    elif type == "tilde":
        rantin = os.popen("/home/karlen/bin/activetilde | shuf -n 1 | sed 's|^|http://tilde.town/~|g'").read().split("\n")
    elif type == "youtube":
      rantin = os.popen ("/home/karlen/bin/mensch -y | shuf -n 1 | awk -F '\t' '{print $3}'").read().split("\n")
    elif type == "link":
      rantin = os.popen ("/home/karlen/bin/mensch -l | shuf -n 1 | awk -F '\t' '{print $3}'").read().split("\n")
    elif type == "gif":
      rantin = os.popen ("/home/karlen/bin/mensch -g | shuf -n 1 | awk -F '\t' '{print $3}'").read().split("\n")
    if 'rantin' in locals():
        for line in rantin:
          if line:
              ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")
    else:
        sendmsg(channel, "Sorry, !random only works with: !random youtube, !random image, !random link, !random gif, !random tilde.")

def famouslastwords(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
   sendmsg(channel, "Sorry, we need the name of one user")
  else:
   name = args[0]
   flw = os.popen("/home/karlen/bin/famouslastwords -v %s" % (name)).read().split("\n")
   for line in flw:
      if line:
          ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def rememberthem(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) >= 1:
   sendmsg(channel, "Sorry, that's too much remembering for me")
  else:
   flw = os.popen("shuf -n 1 ~karlen/reference/zombies").read().split("\n")
   for line in flw:
      if line:
          ircsock.send("PRIVMSG "+ channel + " :" + "pour out a 40 ounce for " + line + " :(" + "\n")

def pondareplay(channel, fmt):
    args = get_text_from_formatted(fmt).split()
    if len(args) == 0:
        flw = os.popen("python /home/karlen/bin/pondareplay --random Y | /home/karlen/bin/pontidy" ).read().split("\n")
    elif len(args) > 0:
        topic = args[0]
        flw = os.popen("python /home/karlen/bin/pondareplay --search %s | /home/karlen/bin/pontidy" % (topic)).read().split("\n")
    for line in flw:
        if line:
          ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")
          time.sleep(0.75)

def chatabout(channel, fmt):
    args = get_text_from_formatted(fmt).split()
    if len(args) == 0:
        sendmsg(channel, "What you want a mention of? TELL ME!")
    elif len(args) > 0:
        topic = args[0]
        flw = os.popen("/home/karlen/bin/mensch -p -w %s | tail -n 3" % (topic)).read().split("\n")
    for line in flw:
        if line:
          ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")
          time.sleep(0.75)

def ircpopularity(channel, fmt):
    args = get_text_from_formatted(fmt).split()
    if len(args) != 2:
        sendmsg(channel, "Sorry, only two combatants are allowed.")
    else:
        fighter1 = args[0]
        fighter2 = args[1]
        quoteaddOut = os.popen("/home/karlen/bin/ircpopularity %s %s" % (fighter1,fighter2)).read().split("\n")
        for line in quoteaddOut:
            if line:
                ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def random_quote_add(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) == 1:
      name = args[0]
      quoteadd = os.popen("/home/karlen/bin/ircquoteadd -u %s" % (name))
  elif len(args) == 2:
      name = args[0]
      number = args[1]
      try:
          int(number)
      except ValueError:
          sendmsg(channel, "Those are not numbers buddy")
      else:
          quoteadd = os.popen("/home/karlen/bin/ircquoteadd -u %s -n %s" % (name,number))
          sendmsg(channel, "That quote was added, thanks!")

def random_quote_screenplay(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 2:
      sendmsg(channel, "We need two integer arguements to start and stop the quote")
  else:
      startswith = args[0]
      endswith = args[1]
      try:
          int(startswith)
      except ValueError:
          sendmsg(channel, "Those are not numbers buddy")
      else:
          try:
              int(endswith)
          except ValueError:
              sendmsg(channel, "Those are not numbers buddy")
          else:
              screenplay_add = os.popen("/home/karlen/bin/ircscreenplay -s %s -e %s" % (startswith,endswith))
              sendmsg(channel, "That irc screenplay was added, thanks!")

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

def say_mentionsof(user, message, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) == 1:
      searchterm = args[0]
      menschnsof = os.popen("/home/karlen/bin/mensch -p -w %s | tail -n 32" % (searchterm)).read().replace("\t", ": ").split("\n")
  elif len(args) == 2:
      searchterm = args[0]
      number = args[1]
      menschnsof = os.popen("/home/karlen/bin/mensch -p -w %s | tail -n %s" % (searchterm,number)).read().replace("\t", ": ").split("\n")
  for mentionof in menschnsof:
    if not "" == mentionof:
      toSend = "PRIVMSG "+ user + " :" + mentionof + "\n"
      if len(toSend) >= 256:
        toSend = toSend[:253] + '...'
      ircsock.send(toSend)

def say_catchup(channel, user, message, fmt):
    args = get_text_from_formatted(fmt).split()
    if len(args) >= 2:
        sendmsg(channel, "Too many arguments, stop arguing!")
    else:
        if len(args) == 0:
            catchups = os.popen("/home/karlen/bin/catchup").read().replace("\t", ": ").split("\n")
            for line in catchups:
                if not "" == line:
                  toSend = "PRIVMSG "+ user + " :" + line + "\n"
                  if len(toSend) >= 256:
                    toSend = toSend[:253] + '...'
                  ircsock.send(toSend)
        elif len(args) == 1:
            numberback = args[0]
            try:
                int(numberback)
            except ValueError:
                sendmsg(channel, "Those are not numbers buddy")
            else:
                catchups = os.popen("/home/karlen/bin/catchup -n %s" % (numberback)).read().replace("\t", ": ").split("\n")
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

def say_cursey(channel):
  curseyOut = os.popen("/home/karlen/bin/cursey").read().split("\n")
  for line in curseyOut:
    if line:
      ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def say_rollcall(channel):
    sendmsg(channel, "quote_bot here! I respond to !quote (!q-apropos, !q-from, !q-add, !q-screenplay), !mentions, !mention-of, !random, !catchup, !chatty, !cursey, !tweet, !haiku, !banter, !famouslastwords, !ircpopularity, !pondareplay, !pourouta40, !chatabout, !commands. Hack my log! ~jumblesale/irc/log")

def do_tweet(channel, fmt):
  text = get_text_from_formatted(fmt)
  chars = len(text)
  if chars > 140:
    ircsock.send("PRIVMSG "+ channel + " :Text has " + str(chars) + " chars, but it must have < 140 to tweet.\n")
  elif chars < 1:
    ircsock.send("PRIVMSG "+ channel +" :I won't tweet nothing.\n")
  else:
    os.popen("echo \"%s\" | tweet > /dev/null" % text)
    sendmsg(channel, "That tweet: '"+ text +"' was some top drawer tweeting, well done")
    
def list_commands(channel):
    sendmsg(channel, "Enter a command proceeded by a !: quote (q-apropos, q-from, q-add, q-screenplay), mentions, mention-of, random, catchup, chatty, cursey, tweet, haiku, banter, famouslastwords, ircpopularity, pondareplay, pourouta40, chatabout commands.")
  
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
  return os.popen("/home/jumblesale/Code/quote_apropos/quote_apropos " + args).read()
  
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

    if ircmsg.find(":!q-add") != -1:
      random_quote_add(options.channel, formatted)

    if ircmsg.find(":!q-screenplay") != -1:
      random_quote_screenplay(options.channel, formatted)

    if ircmsg.find(":!ircpopularity") != -1:
      ircpopularity(options.channel, formatted)

    if ircmsg.find(":!famouslastwords") != -1:
      famouslastwords(options.channel, formatted)

    if ircmsg.find(":!pourouta40") != -1:
      rememberthem(options.channel, formatted)

    if ircmsg.find(":!pondareplay") != -1:
      pondareplay(options.channel, formatted)

    if ircmsg.find(":!chatabout") != -1:
      chatabout(options.channel, formatted)

    if ircmsg.find(":!mentions") != -1:
      say_mentions(user, ircmsg)

    if ircmsg.find(":!mention-of") != -1:
        say_mentionsof(user, ircmsg, formatted)

    if ircmsg.find(":!chatty") != -1:
      say_chatty(options.channel)

    if ircmsg.find(":!cursey") != -1:
      say_cursey(options.channel)

    if ircmsg.find(":!catchup") != -1:
      say_catchup(options.channel, user, ircmsg, formatted)

    if ircmsg.find(":!rollcall") != -1:
      say_rollcall(options.channel)

    if ircmsg.find(":!haiku") != -1:
      haiku(options.channel)

    if ircmsg.find(":!tweet") != -1:
      do_tweet(options.channel, formatted)

    if ircmsg.find(":!commands") != -1:
      list_commands(options.channel)

    if ircmsg.find(":!banter") != -1:
      top_bants(options.channel)

    if ircmsg.find(":!random") != -1:
      random_thing(options.channel, formatted)

    if ircmsg.find("PING :") != -1:
      ping()

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
