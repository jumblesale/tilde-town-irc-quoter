#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import sys
from optparse import OptionParser

import get_users
import mentions

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
  ircsock.send("PRIVMSG "+ channel +" :" + quote + "\n")

def haiku(channel):
  h = os.popen("haiku").read().replace("\n", " // ")
  ircsock.send("PRIVMSG "+ channel +" :" + h + "\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def say_mentions(msg):
  (user, messages) = mentions.find_mentions(msg)
  for mention in messages:
    ircsock.send("PRIVMSG "+ user + " :" + mention + "\n")
  
def listen():
  while 1:

    ircmsg = ircsock.recv(2048)
    ircmsg = ircmsg.strip('\n\r')
    
    print(ircmsg)

    if ircmsg.find(":!quote") != -1:
      random_quote(options.channel)

    if ircmsg.find(":!mentions") != -1:
      say_mentions(ircmsg)

    if ircmsg.find(":!haiku") != -1:
      haiku(options.channel)

    if ircmsg.find("PING :") != -1:
      ping()

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()