#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import subprocess
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
  quote = subprocess.check_output(["/home/karlen/irc/randquote.py"])
  if len(quote) >= 256:
    quote = quote[:253] + '...'
  ircsock.send("PRIVMSG "+ channel +" :" + quote + "\n")

def random_quote_apropos(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    message = "Sorry, q-apropos only accepts 1 argument."
  else:
    if len(args) == 1:
      term = str(args[0])
      message = quote_apropos(channel,term)
  sendmsg(channel, message)

def random_quote_from(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    message = "Sorry, q-from only accepts 1 argument."
  else:
    if len(args) == 1:
      term = str(args[0])
      message = quote_from(channel,term)
  sendmsg(channel, message)

def random_thing(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) != 1:
    sendmsg(channel, "Sorry, !random only works with: !random youtube, !random image, !random link, !random gif, !random tilde.")
  else:
    type = args[0]
    if type == "image":
        rantin = subprocess.check_output(["/home/karlen/bin/qb/ranting.sh", "-i"]).split("\n")
    elif type == "tilde":
        rantin = subprocess.check_output(["/home/karlen/bin/qb/ranting.sh", "-t"]).split("\n")
    elif type == "youtube":
        rantin = subprocess.check_output(["/home/karlen/bin/qb/ranting.sh", "-y"]).split("\n")
    elif type == "link":
        rantin = subprocess.check_output(["/home/karlen/bin/qb/ranting.sh", "-l"]).split("\n")
    elif type == "gif":
        rantin = subprocess.check_output(["/home/karlen/bin/qb/ranting.sh", "-g"]).split("\n")
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
   flw = subprocess.check_output(["/home/karlen/bin/famouslastwords", "-v", name]).split("\n")
   for line in flw:
      if line:
          ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def rememberthem(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) >= 1:
   sendmsg(channel, "Sorry, that's too much remembering for me")
  else:
   flw = subprocess.check_output(["/home/karlen/bin/qb/p40.sh"]).split("\n")
   ircsock.send("PRIVMSG "+ channel + " :" + "pour out a 40 ounce for " + str(flw[0]) + " :(" + "\n")

def pondareplay(channel, fmt):
    args = get_text_from_formatted(fmt).split()
    if len(args) == 0:
        flw = subprocess.check_output(["/home/karlen/bin/qb/pnda.sh","-r"]).split("\n")
    elif len(args) > 0:
        topic = args[0]
        flw = subprocess.check_output(["/home/karlen/bin/qb/pnda.sh","-s",topic]).split("\n")
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
        flw = subprocess.check_output(["/home/karlen/bin/qb/gen.sh","-c",topic]).split("\n")
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
        quoteaddOut = subprocess.check_output(["/home/karlen/bin/qb/gen.sh","-irc",fighter1,fighter2]).split("\n")
        for line in quoteaddOut:
            if line:
                ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def random_quote_add(channel, fmt):
  args = get_text_from_formatted(fmt).split()
  if len(args) == 1:
      name = args[0]
      quoteadd = subprocess.call(["/home/karlen/bin/ircquoteadd","-u",name])
      sendmsg(channel, "That quote was added, thanks!")
  elif len(args) == 2:
      name = args[0]
      number = args[1]
      try:
          int(number)
      except ValueError:
          sendmsg(channel, "Those are not numbers buddy")
      else:
          quoteadd = subprocess.call(["/home/karlen/bin/ircquoteadd","-u",name,"-n",number])
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
              screenplay_add = subprocess.call(["/home/karlen/bin/ircscreenplay","-s",startswith,"-e",endswith])
              sendmsg(channel, "That irc screenplay was added, thanks!")

def haiku(channel):
  h = subprocess.check_output("haiku").replace("\n", " // ")
  ircsock.send("PRIVMSG "+ channel +" :" + h + "\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def say_mentions(user, message):
  nick = get_user_from_message(message)
  menschns = subprocess.check_output(["/home/karlen/bin/mensch","-u",user,"-t","24","-z","+0"]).replace("\t", ": ").split("\n")
  for mention in menschns:
    if not "" == mention:
      toSend = "PRIVMSG "+ nick + " :" + mention + "\n"
      if len(toSend) >= 256:
        toSend = toSend[:253] + '...'
      ircsock.send(toSend)

def say_mentionsof(user, message, fmt):
  args = get_text_from_formatted(fmt).split()
  searchterm = args[0]
  menschnsof = subprocess.check_output(["/home/karlen/bin/qb/gen.sh","-menschnsof",searchterm]).replace("\t", ": ").split("\n")
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
            catchups = subprocess.check_output(["/home/karlen/bin/catchup"]).replace("\t", ": ").split("\n")
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
                catchups = subprocess.check_output(["/home/karlen/bin/catchup","-n", numberback]).read().replace("\t", ": ").split("\n")
                for line in catchups:
                    if not "" == line:
                      toSend = "PRIVMSG "+ user + " :" + line + "\n"
                      if len(toSend) >= 256:
                        toSend = toSend[:253] + '...'
                      ircsock.send(toSend)

def say_chatty(channel):
  chattyOut = subprocess.check_output(["/home/karlen/bin/chatty"]).split("\n")
  for line in chattyOut:
    if line:
      ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def say_cursey(channel):
  curseyOut = subprocess.check_output(["/home/karlen/bin/cursey"]).split("\n")
  for line in curseyOut:
    if line:
      ircsock.send("PRIVMSG "+ channel + " :" + line + "\n")

def say_rollcall(channel):
    sendmsg(channel, "quote_bot here! I respond to !quote (!q-apropos, !q-from, !q-add, !q-screenplay), !mentions, !mention-of, !random, !catchup, !chatty, !cursey, !tweet, !haiku, !famouslastwords, !ircpopularity, !pondareplay, !pourouta40, !chatabout, !tday, !rollcall, !commands. Hack my log! ~jumblesale/irc/log")

def do_tweet(channel, fmt):
  text = get_text_from_formatted(fmt)
  chars = len(text)
  if chars > 140:
    ircsock.send("PRIVMSG "+ channel + " :Text has " + str(chars) + " chars, but it must have < 140 to tweet.\n")
  elif chars < 1:
    ircsock.send("PRIVMSG "+ channel +" :I won't tweet nothing.\n")
  else:
    subprocess.call(["/home/karlen/bin/qb/gen.sh","-tweet",text])
    sendmsg(channel, "That tweet: '"+ text +"' was some top drawer tweeting, well done")

def say_townage(channel):
    townageValue = subprocess.check_output(["/home/karlen/bin/tday"])
    sendmsg(channel, "Happy " + str(townageValue))

def list_commands(channel):
    sendmsg(channel, "I respond to !quote (!q-apropos, !q-from, !q-add, !q-screenplay), !mentions, !mention-of, !random, !catchup, !chatty, !cursey, !tweet, !haiku, !famouslastwords, !ircpopularity, !pondareplay, !pourouta40, !chatabout, !tday, !rollcall, !commands. Hack my log! ~jumblesale/irc/log")
  
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

## INTERFACE TO quote_apropos.hs

def quote_apropos(channel,term):
  quoteApp = subprocess.check_output(["/home/karlen/bin/qb/gen.sh","-qa",term]).split("\n")
  quoteApp = ''.join(quoteApp)
  return str(quoteApp)

def quote_from(channel,user):
  quoteFromOut = subprocess.check_output(["/home/karlen/bin/qb/gen.sh","-qf",user]).split("\n")
  quoteFromOut = ''.join(quoteFromOut)
  return str(quoteFromOut)
  
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

    if ircmsg.find(":!tday") != -1:
      say_townage(options.channel)

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

    if ircmsg.find(":!random") != -1:
      random_thing(options.channel, formatted)

    if ircmsg.find("PING :") != -1:
      ping()

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
