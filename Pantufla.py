import socket
import time
import sys

## Cosas utiles:
HOST = "127.0.0.1"
PORT = 27960
RCONPWD = "test"

SERVERLOG = "C:\Apps\URT41\q3ut4\zappa.log"
ADMINLIST = "C:\Apps\URT41\q3ut4\pepe.txt"
CYCLEMAP = "C:\Apps\URT41\q3ut4\zappa_maps.txt"

HEAD = "\xFF\xFF\xFF\xFFrcon "
BOT = "say ^7[^4Pantufla^7] "

VERMSG = "^7[^4Pantufla^7] Version 0.2 - by Mr.PanNegro - Inicializando..."
WELCOME = "Hola, aqui estoy, a su servicio."

## Super Parser (procurar que no se haga enorme)
def parser_cmd(say):
	text = say.lstrip().split(" ")
	if len(text) < 2:
		print "DEBUG: Bad line"
		return False
	print "DEBUG: Captured event: "+text[1]
	#text[0] = Tiempo
	#text[1] = Evento
	#text[2] = Player Number
	#text[3] = Player Name
	#text[4] = Comando
	#text[5,..] = Argumentos	
	if "ClientConnect:" in text[1]:
		greeting(text[2])
	if "say:" in text[1]:
		comando = text[4].rstrip("\n")
		player = text[3]
		playernum = text[2]
		print "DEBUG: SAY detected: by " + player + " " + comando
		if comando == "!anew":
			cmd_anew(player, playernum)
		if comando == "!pantufla":
			cmd_pantufla(playernum)
		if comando == "!admin":
			if len(text) > 5: cmd_admin(playernum, text[5])
		if comando == "!recargar":
			cmd_recargar(playernum)
		if comando == "!reiniciar":
			cmd_reiniciar(playernum)
		if comando == "!kick" or comando == "!k":
			if len(text) > 5: cmd_kick(playernum, text[5])
		if comando == "!slap":
			if len(text) > 5: cmd_slap(playernum, text[5])
		if comando == "!nuke":
			if len(text) > 5: cmd_nuke(playernum, text[5])
		if comando == "!map":
			if len(text) > 5: cmd_map(playernum, text[5])
		if comando == "!nextmap":
			if len(text) > 5: cmd_nextmap(playernum, text[5])
			else: cmd_nextmap(playernum, None)
		if comando == "!cerrado":
			if len(text) > 5: cmd_matchmode(playernum, text[5])
		if comando == "!publico":
			if len(text) > 5: cmd_publicmode(playernum, text[5])

## La parte que se comunica con el servidor.
def send_rcon(comando): #Devuelve lo que responda el server.
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#print HEAD+RCONPWD+" "+comando #Solo para dumpear.
	sock.sendto(HEAD+RCONPWD+" "+comando,(HOST,PORT))
	buffer = sock.recv(1024)
	sock.close()
	time.sleep(0.5)
	return buffer

## Funcion que chequea si el player number es admin o no.
def check_admin(pnumber): #True = Admin; False = NO
	print "DEBUG: Checking ADMIN permissions..."
	ID = send_rcon("dumpuser "+pnumber).split("\n") #Dumpuser tira TODA la info sobre el PlayerNumber.
	fp2 = open(ADMINLIST, 'r')
	for i in range(10,len(ID)-1):
		#print ID
		buf = ID[i].split()
		if buf[0] == "cl_guid": #De toda la info que nos da, buscamos la del GUID/Qkey
			while True:
				fpline = fp2.readline()
				if buf[1] == fpline.rstrip("\n"): #La comparamos con nuestra listita (sin \n)
					fp2.close()
					return True;
				if not fpline: break
	fp2.close()

## Esto esta solo puesto para saludar a mi nick.
def greeting(pnumber):
	print "DEBUG: Checking greetings for user..."
	ID = send_rcon("dumpuser "+pnumber).split("\n")
	for i in range(10,len(ID)-2):
		buf = ID[i].split()
		if buf[0] == "cl_guid": #De toda la info que nos da, buscamos la del GUID/Qkey
			if buf[1] == "9BDC2102493CD06226A4509D5F3B2242": send_rcon(BOT+"^2Mr.PanNegro ^7is in da house!")

## Puro easteregg.
def cmd_anew(player, pnumber):
	if check_admin(pnumber): send_rcon(BOT+player+" :3")
def cmd_pantufla(pnumber):
	if check_admin(pnumber): send_rcon(BOT+"Que bien que anda este bot niggas.")
			
## Permite un admin agregar a otro admin
def cmd_admin(pnumber, player):
	if check_admin(pnumber):
		print "DEBUG: Command ADMIN executed"
		player = player.rstrip("\n") #El comando seguramente viene con \n, quitarselo.
		statuslist = send_rcon("status").split("\n")
		for i in range(4,len(statuslist)-2):
			#[0]=Number [1]=Score [2]=Ping [3]=Name [4]=Lastmsg [5]=IP [6]=QPort [7]=Rate
			buf = statuslist[i].split()
			if player in buf[3]: #Si el nombre concuerda con alguien
				ID = send_rcon("dumpuser "+buf[0]).split("\n") #Buscamos la GUID de ese player
				for j in range(10,len(ID)-1):
					buf2 = ID[j].split()
					if buf2[0] == "cl_guid":
						print "cl_guid encontrado!"
						fpadmin = open(ADMINLIST, 'a')
						fpadmin.write("#"+buf[3].rstrip("^7")+"\n"+buf2[1]+"\n") #Volcamos al archivo un #Nick\nGUID
						fpadmin.close()
						send_rcon(BOT+"Demos la bienvenida a un nuevo admin: ^2"+buf[3]) #Notificamos el hecho
						print "[Pantufla]: "+buf[3]+" AGREGADO A ADMINS!"
						return True #Salimos.
		send_rcon(BOT+" No hay ningun jugador con ese nombre.")
		return False
	else: print "DEBUG: Command ADMIN rejected, no admin"

## Para recargar la config y reiniciar el servidor.
def cmd_recargar(pnumber):
	if check_admin(pnumber):
		print "DEBUG: Command RECARGAR executed"
		send_rcon(BOT+" Reiniciando el servidor...")
		send_rcon("reload")
	else: print "DEBUG: Command RECARGAR rejected, no admin"

## Para reiniciar la partida solamente.
def cmd_reiniciar(pnumber):
	if check_admin(pnumber):
		print "DEBUG: Command REINICIAR executed"
		send_rcon(BOT+" Reiniciando el mapa actual.")
		send_rcon("restart")
	else: print "DEBUG: Command REINICIAR rejected, no admin"

## Kick a un player, ya sea por PlayerName o PlayerNumber
def cmd_kick(pnumber, pkicked):
	if check_admin(pnumber):
		print "DEBUG: Command KICK executed"
		pkicked = pkicked.rstrip("\n") #El comando probablemente venga con \n.
		statuslist = send_rcon("status").split("\n")
		#if "@" in pkicked: #Kick por @PlayerNumber
			#print "@ detected"
			#send_rcon("kick "+pkicked.replace("@", ""))
		#else: #Kick por PlayerName
		for i in range(4,len(statuslist)-2):
			#[0]=Number [1]=Score [2]=Ping [3]=Name [4]=Lastmsg [5]=IP [6]=QPort [7]=Rate
			buf = statuslist[i].split()
			if pkicked in buf[3]:
				send_rcon("kick "+buf[0]) #Kickea al playernumber.
				print "Debug: "+buf[3]+" KICKED!"
	else: print "DEBUG: Command KICK rejected, no admin"

## Comando para slappear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_slap(pnumber, pslapped):
	if check_admin(pnumber):
		print "DEBUG: Command SLAP executed"
		pslapped = pslapped.rstrip("\n") #El comando probablemente venga con \n.
		statuslist = send_rcon("status").split("\n")
		#if "@" in pslapped: #Slap por @PlayerNumber
			#print "@ detected"
			#send_rcon("slap "+pslapped.replace("@", ""))
		#else: #Slap por PlayerName
		for i in range(4,len(statuslist)-2):
			#[0]=Number [1]=Score [2]=Ping [3]=Name [4]=Lastmsg [5]=IP [6]=QPort [7]=Rate
			buf = statuslist[i].split()
			if pslapped in buf[3]:
				send_rcon("slap "+buf[0]) #Slapea al playernumber.
				print "Debug: "+buf[3]+" SLAPPED!"
	else: print "DEBUG: Command SLAP rejected, no admin"

## Comando para nukear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_nuke(pnumber, pnuked):
	if check_admin(pnumber):
		print "DEBUG: Command NUKE executed"
		pnuked = pnuked.rstrip("\n") #El comando probablemente venga con \n.
		statuslist = send_rcon("status").split("\n")
		#if "@" in pnuked: #Nuke por @PlayerNumber
			#print "@ detected"
			#send_rcon("nuke "+pnuked.replace("@", ""))
		#else: #Nuke por PlayerName
		for i in range(4,len(statuslist)-2):
			#[0]=Number [1]=Score [2]=Ping [3]=Name [4]=Lastmsg [5]=IP [6]=QPort [7]=Rate
			buf = statuslist[i].split()
			if pnuked in buf[3]:
				send_rcon("nuke "+buf[0]) #Nuke al playernumber.
				print "Debug: "+buf[3]+" NUKED!"
	else: print "DEBUG: Command NUKE rejected, no admin"

## Comando para cambiar el mapa instantaneamente.
def cmd_map(pnumber, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(pnumber):
		print "DEBUG: Command MAP executed"
		mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
		with open(CYCLEMAP, 'r') as fmap:
			availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
		fmap.close()
		for x in range(len(availablemaps)):
			if mapname in availablemaps[x]:
				send_rcon(BOT+" Cambiando el mapa a "+availablemaps[x])
				time.sleep(3)
				send_rcon("map "+availablemaps[x]) #Si el mapa esta en el cycle, cambiar.
				return True
		send_rcon(BOT+" No encuentro ningun mapa con ese nombre.")
		return False
	else: print "DEBUG: Command MAP rejected, no admin"

## Comando para ver y cambiar el mapa siguiente.
def cmd_nextmap(pnumber, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(pnumber):
		print "DEBUG: Command NEXTMAP executed"
		if mapname == None:
			#Habria que implementar que diga el nextmap
			return False
		else:
			mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
			with open(CYCLEMAP, 'r') as fmap:
				availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
			fmap.close()
			for x in range(len(availablemaps)):
				if mapname in availablemaps[x]:
					send_rcon(BOT+" Cambiando el mapa SIGUIENTE a "+availablemaps[x])
					send_rcon("g_nextmap "+availablemaps[x]) #Si el mapa esta en el cycle, cambiar.
					return True
			send_rcon(BOT+" No encuentro ningun mapa con ese nombre.")
			return False
	else: print "DEBUG: Command NEXTMAP rejected, no admin"

def cmd_matchmode(pnumber, mode):
	if check_admin(pnumber):
		print "DEBUG: Command CERRADO executed"
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon(BOT+" Cerrando el server para un partido de TS...")
			send_rcon(BOT+" Reglas del juego cargadas: ^2UrTLA TS")
			send_rcon("exec zappa_urtlats.cfg")
			time.sleep(3)
			send_rcon(BOT+" Por favor, elegir un mapa para empezar.")
			return True
		if mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon(BOT+" No tengo la config para jugar un partido de CTF.")
			return False
		send_rcon(BOT+" No tengo disponible ese modo de juego.")
		return False
	else: print "DEBUG: Command CERRADO rejected, no admin"

def cmd_publicmode(pnumber, mode):
	if check_admin(pnumber):
		print "DEBUG: Command PUBLICO executed"
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon(BOT+" Abriendo el server en modo TS.")
			time.sleep(1)
			send_rcon("exec zappa.cfg")
			return True
		if mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon(BOT+" No tengo la config para poner el server en CTF.")
			return False
		send_rcon(BOT+" No tengo disponible ese modo de juego.")
		return False
	else: print "DEBUG: Command PUBLICO rejected, no admin"
	
## Principal:
if __name__ == "__main__":
	print "[Pantufla]: Initializing program... OK."

	# Inicializacion del socket y mandamos nuestros primeros mensajes.
	send_rcon(VERMSG)
	send_rcon(BOT+WELCOME)
	print "[Pantufla]: Enviando bienvenida... OK."

	# Abrimos el log del server de urt y buscamos el EOF
	fp = open(SERVERLOG, 'r')
	while True:
		new = fp.readline()
		if not new: break
	print "[Pantufla]: Log cargado, listo para parsear ordenes..."

	# Recibimos lineas nuevas en tiempo CASI real y las parseamos.
	while True:
		time.sleep(0.001)
		new = fp.readline()
		if new:
			parser_cmd(new)
	
	# Si de alguna manera se llega a este lugar, salir limpio.
	fp.close()
	print "[Pantufla]: Exiting..."