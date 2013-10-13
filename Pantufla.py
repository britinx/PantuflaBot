import socket
import time
import sys
import sqlite3 as lite

## Inicializacion:
HEAD = "\xFF\xFF\xFF\xFFrcon "
BOT = "say ^7[^4Pantufla^7] "
VERMSG = "^7[^4Pantufla^7] Version 0.3.1 - by Mr.PanNegro - Inicializando..."
WELCOME = "Hola, aqui estoy, a su servicio."

CONFIG = "Pantufla.cfg"
HOST = ""
PORT = ""
RCONPWD = ""
SERVERLOG = ""
CYCLEMAP = ""

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
	if "ClientUserinfoChanged:" in text[1]:
		check_player(text[2])
	if "say:" in text[1]:
		comando = text[4].rstrip("\n")
		player = text[3]
		playernum = text[2]
		print "DEBUG: SAY detected: by " + player + " " + comando
		if comando == "!anew":
			cmd_anew(player, playernum)
		if comando == "!pantufla":
			cmd_pantufla(playernum)
		if comando == "!admin": #Siempre chequear el 5to argumento, es obligatorio.
			if len(text) > 5: cmd_admin(playernum, text[5])
		if comando == "!alias":
			if len(text) > 5: cmd_alias(playernum, text[5])
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

## Funcion que devuelve la GUID solo con el PlayerNumber
def searchguid(playernum): #Si no encuentra = False
	ID = send_rcon("dumpuser "+playernum).split("\n") #Dumpuser tira TODA la info sobre el PlayerNumber.
	for i in range(10,len(ID)-1): #La GUID nunca esta entre las primeras 10 lineas del dumpuser, y la ultima es NULL.
		buf = ID[i].split()
		if buf[0] == "cl_guid": #De toda la info que nos da, buscamos la del GUID/Qkey
			return buf[1] #Devolvemos el valor de cl_guid.
	return False

## Funcion que devuelve el PlayerNumber y PlayerName, con solo una parte del nombre.
def searchplayer(partialname): #Si no encuentra = 0,False
	partialname = partialname.rstrip("\n") #El comando seguramente viene con \n, quitarselo.
	statuslist = send_rcon("status").split("\n") #Ordenamos el playerlist
	for i in range(4,len(statuslist)-2):
	#[0]=Number [1]=Score [2]=Ping [3]=Name [4]=Lastmsg [5]=IP [6]=QPort [7]=Rate
		buf = statuslist[i].split()
		if partialname in buf[3]: #Si el nombre concuerda con alguien del playerlist
			return buf[0],buf[3]
	return 0,False

## Funcion que chequea si el player number es admin o no.
def check_admin(playernum): #True = Admin; False = NO
	print "DEBUG: Checking ADMIN permissions..."
	guid = searchguid(playernum)
	dbcursor.execute("SELECT * FROM Players WHERE Guid=? AND Level>=5", (guid,))
	row = dbcursor.fetchone()
	if guid == row[2]: #La comparamos con nuestra db.
		return True
	if not row: return False

## Cada vez que ingresa un player, comparar con la DB
def check_player(playernum): #Devuelve NULL
	print "DEBUG: Checking user info changed..."
	ID = send_rcon("dumpuser "+playernum).split("\n")
	for i in range(3,len(ID)-1):
		buf = ID[i].split()
		if buf[0] == "name": playername = buf[1] #De toda la info buscamos el nick
		if buf[0] == "cl_guid": playerguid = buf[1] #y su GUID
	if playerguid:
		dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (playerguid,)) #Chequeamos si la GUID ya esta guardada
		row = dbcursor.fetchone()
		if row == None:
			print "DEBUG: Player nuevo, agregando a la DB..."
			dbcursor.execute("INSERT INTO Players (Name, Guid, Level) VALUES(?,?,0)",(playername,playerguid))
			dbconnection.commit() #Si no esta guardada, la agregamos.
		else:
			print "DEBUG: Player conocido, no se agrega a la DB." #Si esta guardada, saltamos.
			dbcursor.execute("SELECT * FROM Aliases WHERE ID=?", (row[0],))
			while True:
				aliasrow = dbcursor.fetchone()
				if aliasrow == None: #Buscamos sus aliases y los guardamos
					dbcursor.execute("INSERT INTO Aliases VALUES(?,?)",(row[0],playername))
					dbconnection.commit()
					break
				if aliasrow[1] == playername: break

## Puro easteregg.
def cmd_anew(playername, playernum):
	if check_admin(playernum): send_rcon(BOT+playername+" :3")
def cmd_pantufla(playernum):
	if check_admin(playernum): send_rcon(BOT+"Que bien que anda este bot niggas.")
			
## Permite un admin agregar a otro admin
def cmd_admin(caller, partialname):
	if check_admin(caller):
		print "DEBUG: Command ADMIN executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			guid = searchguid(playernumber) #Solicitamos su GUID
			dbcursor.execute("UPDATE Players SET Level=10 WHERE Guid=?",(guid,))
			dbconnection.commit() #Le modificamos el Level en la DB.
			send_rcon(BOT+"Nuevo admin en el sistema: ^2"+playername) #Notificamos el hecho
			print "[Pantufla]: "+playername+" AGREGADO A ADMINS!"
			return True #Salimos.
		else:
			send_rcon(BOT+" No hay ningun jugador con ese nombre.")
			return False
	else: print "DEBUG: Command ADMIN rejected, no admin"

## Permite buscar aliases de los players en la DB
def cmd_alias(caller, partialname):
	if check_admin(caller):
		print "DEBUG: Command ALIAS executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			guid = searchguid(playernumber) #Solicitamos su GUID
			dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (guid,)) #Pedimos la info de esa GUID
			row = dbcursor.fetchone()
			dbcursor.execute("SELECT * FROM Aliases WHERE ID=?", (row[0],)) #La lista de aliases para ese ID.
			rows = dbcursor.fetchall()
			send_rcon(BOT+"Aliases de "+playername+": ")
			for rowaliases in rows: send_rcon(BOT+rowaliases[1]) #Los tiramos uno por renglon.
			return True
		else:
			send_rcon(BOT+" No hay ningun jugador con ese nombre.")
			return False
	else: print "DEBUG: Command ALIAS rejected, no admin"

## Para recargar la config y reiniciar el servidor.
def cmd_recargar(caller):
	if check_admin(caller):
		print "DEBUG: Command RECARGAR executed"
		send_rcon(BOT+" Reiniciando el servidor...")
		send_rcon("reload")
	else: print "DEBUG: Command RECARGAR rejected, no admin"

## Para reiniciar la partida solamente.
def cmd_reiniciar(caller):
	if check_admin(caller):
		print "DEBUG: Command REINICIAR executed"
		send_rcon(BOT+" Reiniciando el mapa actual.")
		send_rcon("restart")
	else: print "DEBUG: Command REINICIAR rejected, no admin"

## Kick a un player, ya sea por PlayerName o PlayerNumber
def cmd_kick(caller, partialname):
	if check_admin(caller):
		print "DEBUG: Command KICK executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("kick "+playernumber) #Kickea al playernumber.
			print "Debug: "+playername+" KICKED!"
	else: print "DEBUG: Command KICK rejected, no admin"

## Comando para slappear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_slap(caller, partialname):
	if check_admin(caller):
		print "DEBUG: Command SLAP executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("slap "+playernumber) #Slapea al playernumber.
			print "Debug: "+playername+" SLAPPED!"
	else: print "DEBUG: Command SLAP rejected, no admin"

## Comando para nukear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_nuke(caller, partialname):
	if check_admin(caller):
		print "DEBUG: Command NUKE executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("nuke "+playernumber) #Nuke al playernumber.
			print "Debug: "+playername+" NUKED!"
	else: print "DEBUG: Command NUKE rejected, no admin"

## Comando para cambiar el mapa instantaneamente.
def cmd_map(caller, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(caller):
		print "DEBUG: Command MAP executed"
		mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
		with open(CYCLEMAP, 'r') as fmap: availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
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
def cmd_nextmap(caller, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(caller):
		print "DEBUG: Command NEXTMAP executed"
		if mapname == None:
			#Habria que implementar que diga el nextmap
			return False
		else:
			mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
			with open(CYCLEMAP, 'r') as fmap: availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
			fmap.close()
			for x in range(len(availablemaps)):
				if mapname in availablemaps[x]:
					send_rcon(BOT+" Cambiando el mapa SIGUIENTE a "+availablemaps[x])
					send_rcon("g_nextmap "+availablemaps[x]) #Si el mapa esta en el cycle, cambiar.
					return True
			send_rcon(BOT+" No encuentro ningun mapa con ese nombre.")
			return False
	else: print "DEBUG: Command NEXTMAP rejected, no admin"

## Comando para iniciar el matchmode:
def cmd_matchmode(caller, mode): #True = Listo para empezar; False = Error.
	if check_admin(caller):
		print "DEBUG: Command CERRADO executed" #Va con argumento (TS, CTF, etc...)
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon(BOT+" Cerrando el server para un partido de TS...")
			send_rcon(BOT+" Reglas del juego cargadas: ^2UrTLA TS")
			send_rcon("exec zappa_urtlats.cfg")
			time.sleep(3) #Hacemos tiempo porque los players son luisitos.
			send_rcon(BOT+" Por favor, elegir un mapa para empezar.")
			return True
		if mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon(BOT+" No tengo la config para jugar un partido de CTF.")
			return False #Esto esta hardcodeado, pero deberia agregarse.
		send_rcon(BOT+" No tengo disponible ese modo de juego.")
		return False
	else: print "DEBUG: Command CERRADO rejected, no admin"

## Comando para hacer publico el server:
def cmd_publicmode(caller, mode): #True = Listo para empezar; False = Error.
	if check_admin(caller):
		print "DEBUG: Command PUBLICO executed" #Va con argumento (TS, CTF, etc...)
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon(BOT+" Abriendo el server en modo TS.")
			time.sleep(1)
			send_rcon("exec zappa.cfg")
			return True
		if mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon(BOT+" No tengo la config para poner el server en CTF.")
			return False #Esto esta hardcodeado, pero deberia agregarse.
		send_rcon(BOT+" No tengo disponible ese modo de juego.")
		return False
	else: print "DEBUG: Command PUBLICO rejected, no admin"
	
## Principal:
if __name__ == "__main__":
	try: # Inicializacion de la DB
		dbconnection = lite.connect("Pantufla.db")
		dbconnection.text_factory = str
		dbcursor = dbconnection.cursor()
		#dbcursor.execute("DROP TABLE IF EXISTS Players") #Solo para eliminar las tablas
		#dbcursor.execute("DROP TABLE IF EXISTS Aliases") #en caso de error o prueba.
		dbcursor.execute("CREATE TABLE IF NOT EXISTS Players(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Guid TEXT, Level INT)")
		dbcursor.execute("CREATE TABLE IF NOT EXISTS Aliases(ID INT, ALIAS TEXT)")
	except lite.Error, e:
		print "ERROR: %s:" % e.args[0]
		sys.exit(1)

	# Cargamos el archivo de config.
	fconfig = open(CONFIG, 'r')
	while True:
		configline = fconfig.readline().split()
		if not configline: break
		else:
			if configline[0] == "HOST": HOST = configline[2]
			if configline[0] == "PORT": PORT = int(configline[2])
			if configline[0] == "PASSWORD": RCONPWD = configline[2]
			if configline[0] == "SERVERLOG": SERVERLOG = configline[2]
			if configline[0] == "CYCLEMAP": CYCLEMAP = configline[2]
	print "[Pantufla]: Inicializando programa... OK."

	# Inicializacion del socket y mandamos nuestros primeros mensajes.
	send_rcon(VERMSG)
	#send_rcon(BOT+WELCOME)
	print "[Pantufla]: Enviando bienvenida... OK."

	# Abrimos el log del server de urt y buscamos el EOF
	fp = open(SERVERLOG, 'r')
	while True:
		new = fp.readline()
		if not new: break
	print "[Pantufla]: Log cargado, listo para parsear ordenes..."

	# Recibimos lineas nuevas en tiempo real de mentira y las parseamos.
	while True:
		time.sleep(0.01)
		new = fp.readline()
		if new: parser_cmd(new)
	
	# Si de alguna manera se llega a este lugar, salir limpio.
	fp.close()
	print "[Pantufla]: Saliendo..."
