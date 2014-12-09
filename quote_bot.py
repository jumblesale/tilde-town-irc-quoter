#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
from optparse import OptionParser

import get_users

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#tildetown',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='quote_bot',
                  help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()


def ping(): # This is our first function! It will respond to server Pings.
  ircsock.send("PONG :pingis\n")  

def sendmsg(chan , msg): # This is the send message function, it simply sends messages to the channel.
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n") 

def joinchan(chan): # This function is used to join channels.
  ircsock.send("JOIN "+ chan +"\n")

def hello(): # This function responds to a user that inputs "Hello Mybot"
  ircsock.send("PRIVMSG "+ channel +" :Hello!\n")

def random_quote(channel):
  quote = os.popen("/home/frs/quotes/randquote.py").read()
  ircsock.send("PRIVMSG "+ channel +" :" + quote + "\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

  joinchan(channel) # Join the channel using the functions we previously defined

def mentions(msg):
  print msg

  
def listen():
  while 1: # Be careful with these! it might send you to an infinite loop
    

    ircmsg = ircsock.recv(2048) # receive data from the server
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    
    print ircmsg

    if ircmsg.find(":!quote") != -1: # If someone says !quote
      random_quote()

    if ircmsg.find(":!mentions") != -1:
        mentions(ircmsg)

    if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
      ping()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()