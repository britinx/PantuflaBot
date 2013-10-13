import socket
import time
import sys

## Cosas utiles:
HOST = "127.0.0.1"
PORT = 27960
RCONPWD = "test"

HEAD = "\xFF\xFF\xFF\xFFrcon "
BOT = " say ^7[^4Pantufla ^2(BETA)^7] "

VERMSG = HEAD + RCONPWD + " ^7[^4Pantufla^7] Version 0.1 - by Mr.PanNegro - Inicializando..."
WELCOME = HEAD + RCONPWD + BOT + "Hola, aqui estoy, a su servicio."

## Super Parser (procurar que no se haga enorme)
def parser_cmd(say):
	text = say.lstrip().split(" ")
	if len(text) < 2:
		print "DEBUG: Bad line"
		return 1
	print "DEBUG: Captured event: "+text[1]
	if "say:" in text[1]:
		print "SAY detected: by "+text[3]+" "+ text[4]
		if text[4] == "!anew\n":
			cmd_anew(text[3])
		if text[4] == "!admin\n":
			cmd_admin(text[3], text[2])
		if text[4] == "!kick":
			cmd_kick(text[2], text[5])

def check_admin(pnumber):
	print "DEBUG: Checking ADMIN permissions..."
	sock.sendto(HEAD+RCONPWD+" dumpuser "+pnumber, (HOST, PORT))
	ID = sock.recv(1024).split("\n")
	time.sleep(0.5)
	ID = ID[28].split()
	print ID
	if ID[1] == "08F6B558185486DA3F0D995DE4E2AF19":
		return True;
	else:
		return False;

def cmd_anew(player):
	sock.sendto(HEAD+RCONPWD+BOT+player+" :3",(HOST,PORT))
	sock.recv(1024)
	time.sleep(0.5)
			
## Check si el player es administrador o no:
def cmd_admin(player, pnumber):
	if check_admin(pnumber):
		sock.sendto(HEAD+RCONPWD+BOT+player+" Ud. es administrador", (HOST, PORT))
	else:
		sock.sendto(HEAD+RCONPWD+BOT+player+" Ud. NO es administrador", (HOST, PORT))
	sock.recv(1024)
	time.sleep(0.5)

def cmd_kick(pnumber, pkicked):
	if check_admin(pnumber):
		print "DEBUG: Command KICK executed"
		sock.sendto(HEAD+RCONPWD+" kick "+pkicked, (HOST, PORT))
		sock.recv(1024)
		time.sleep(0.5)
		#sock.sendto(HEAD+RCONPWD+" status", (HOST, PORT))
		#list = sock.recv(1024).split("\n")
		#for i in range(4,len(list)-2):
			#playerinfo = list[i].split()
			#print playerinfo[3]
		#time.sleep(0.5)
	else:
		print "DEBUG: Command KICK rejected, no admin"
	
## Principal:
if __name__ == "__main__":
	print "[Pantufla]: Starting... OK."

	# Inicializacion del socket y mandamos nuestros primeros mensajes.
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(VERMSG, (HOST, PORT))
	sock.recv(1024)
	time.sleep(0.5)
	sock.sendto(WELCOME, (HOST, PORT))
	sock.recv(1024)
	time.sleep(0.5)
	print "[Pantufla]: Welcome... OK."

	# Abrimos el log del server de urt y buscamos el EOF
	fp = open("C:\Apps\URT41\q3ut4\zappa.log", 'r')
	while True:
		new = fp.readline()
		if not new: break
	print "[Pantufla]: Log loaded, ready to parse text..."

	# Recibimos lineas nuevas en tiempo CASI real y las parseamos.
	while True:
		time.sleep(0.001)
		new = fp.readline()
		if new:
			parser_cmd(new)
	
	# Si de alguna manera se llega a este lugar, salir limpio.
	fp.close()
	print "[Pantufla]: Exiting..."