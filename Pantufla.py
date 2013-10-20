import socket
import time
import sys
import sqlite3 as lite
from random import choice

## Inicializacion:
HEAD = "\xFF\xFF\xFF\xFFrcon"
BOT = "say ^7[^4Pantufla^7]"
VERMSG = "^7[^4Pantufla^7] Version 0.4b - by Mr.PanNegro - Inicializando..."

FCONFIG = "Pantufla.cfg"
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
	print "DEBUG: Captured event: %s" %(text[1])
	#text[0] = Tiempo
	#text[1] = Evento
	#text[2] = Player Number
	#text[3] = Player Name
	#text[4] = Comando
	#text[5,..] = Argumentos	
	if "ClientUserinfo:" in text[1]:
		check_player(text[2])
	elif "say:" in text[1]:
		comando = text[4].rstrip("\n")
		player = text[3]
		playernum = text[2]
		print "DEBUG: SAY detected: by %s %s" %(player,comando)
		if comando == "!anew":
			cmd_anew(player, playernum)
		elif comando == "!pantufla":
			cmd_pantufla(playernum)
		elif comando == "!admin": #Siempre chequear el 5to argumento, es obligatorio.
			if len(text) > 6: cmd_admin(playernum, text[5], text[6])
		elif comando == "!alias":
			if len(text) > 5: cmd_alias(playernum, text[5])
		elif comando == "!force":
			if len(text) > 6: cmd_force(playernum, text[5], text[6])
		elif comando == "!id":
			if len(text) > 5: cmd_id(playernum, text[5])
		elif comando == "!recargar":
			cmd_recargar(playernum)
		elif comando == "!reiniciar":
			cmd_reiniciar(playernum)
		elif comando == "!teams":
			cmd_teams(playernum)
		elif comando == "!kick" or comando == "!k":
			if len(text) > 5: cmd_kick(playernum, text[5])
		elif comando == "!ban":
			if len(text) > 6: cmd_ban(playernum, text[5], text[6])
		elif comando == "!unban":
			if len(text) > 5: cmd_unban(playernum, text[5])
		elif comando == "!slap":
			if len(text) > 5: cmd_slap(playernum, text[5])
		elif comando == "!nuke":
			if len(text) > 5: cmd_nuke(playernum, text[5])
		elif comando == "!mute":
			if len(text) > 5: cmd_mute(playernum, text[5])
		elif comando == "!map":
			if len(text) > 5: cmd_map(playernum, text[5])
		elif comando == "!nextmap":
			if len(text) > 5: cmd_nextmap(playernum, text[5])
			else: cmd_nextmap(playernum, None)
		elif comando == "!cerrado":
			if len(text) > 5: cmd_matchmode(playernum, text[5])
		elif comando == "!publico":
			if len(text) > 5: cmd_publicmode(playernum, text[5])

## La parte que se comunica con el servidor.
def send_rcon(comando): #Devuelve lo que responda el server.
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#print "%s %s %s" %(HEAD,RCONPWD,comando) #Solo para dumpear.
	try:
		sock.sendto("%s %s %s" %(HEAD,RCONPWD,comando), (HOST,PORT))
		buffer = sock.recv(1024)
		sock.close()
	except Exception, e:
		if sock:
			sock.close()
		print "ERROR %s: Problemas en la conexion con el servidor." %e.args[0]
		sys.exit(1)
	time.sleep(0.5)
	return buffer

## Funcion que devuelve la GUID solo con el PlayerNumber
def searchguid(playernum): #Si no encuentra = False
	ID = send_rcon("dumpuser %s" %playernum).split("\n") #Dumpuser tira TODA la info sobre el PlayerNumber.
	for i in range(10,len(ID)-1): #La GUID nunca esta entre las primeras 10 lineas del dumpuser, y la ultima es NULL.
		buf = ID[i].split()
		if buf[0] == "cl_guid": #De toda la info que nos da, buscamos la del GUID/Qkey
			return buf[1] #Devolvemos el valor de cl_guid.
	return False

## Funcion que devuelve el PlayerNumber y PlayerName, con solo una parte del nombre.
def searchplayer(partialname): #Si no encuentra = 0,False
	partialname = partialname.rstrip("\n") #El comando seguramente viene con \n, quitarselo.
	if partialname[:1] == "@":
		partialname = partialname[1:]
		dbcursor.execute("SELECT * FROM Players WHERE ID=?", (partialname,))
		row = dbcursor.fetchone()
		if row == None: return 0,False
		else: return row[0],"ID"
	else:
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
	if not row: return False
	elif guid == row[2]: #La comparamos con nuestra db.
		return row[3]

## Cada vez que ingresa un player, comparar con la DB
def check_player(playernum): #Devuelve NULL
	print "DEBUG: Checking user info changed..."
	ID = send_rcon("dumpuser %s" %playernum).split("\n")
	for i in range(3,len(ID)-1):
		buf = ID[i].split()
		if buf[0] == "name": playername = buf[1] #De toda la info buscamos el nick
		elif buf[0] == "cl_guid": playerguid = buf[1] #y su GUID
	if playerguid:
		# Chequeamos si el player es nuevo.
		dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (playerguid,)) #Chequeamos si la GUID ya esta guardada
		row = dbcursor.fetchone()
		if row == None:
			print "DEBUG: Player nuevo, agregando a la DB..."
			dbcursor.execute("INSERT INTO Players (Name, Guid, Level) VALUES(?,?,0)",(playername,playerguid))
			dbconnection.commit() #Si no esta guardada, la agregamos.
			dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (playerguid,)) #Pedimos la GUID nuevamente.
			row = dbcursor.fetchone()
		else: print "DEBUG: Player conocido, no se agrega a la DB." #Si esta guardada, saltamos.
		# Buscamos los aliases del player.
		dbcursor.execute("SELECT * FROM Aliases WHERE ID=?", (row[0],))
		while True:
			aliasrow = dbcursor.fetchone()
			if aliasrow == None: #Buscamos sus aliases y los guardamos
				dbcursor.execute("INSERT INTO Aliases VALUES(?,?)",(row[0],playername))
				dbconnection.commit()
				break
			elif aliasrow[1] == playername: break
		# Buscamos si el player esta banneado.
		dbcursor.execute("SELECT * FROM Bans WHERE ID=?", (row[0],))
		bansrow = dbcursor.fetchone()
		if bansrow == None: print "DEBUG: Player habilitado para jugar."
		else:
			if bansrow[2] == 0:
				send_rcon("kick %s" %playernum)
				print "DEBUG: Player %s no habilitado para jugar." %playername
			else:
				print "DEBUG: Ban temporal no implementado."
		return True	

## Puro easteregg.
def cmd_anew(playername, playernum):
	if check_admin(playernum) == 10: send_rcon("%s %s :3" %(BOT,playername))
def cmd_pantufla(playernum):
	if check_admin(playernum) == 10: send_rcon("%s Que bien que anda este bot niggas." %BOT)
			
## Permite un admin agregar a otro admin
def cmd_admin(caller, partialname, level):
	if check_admin(caller) == 10:
		print "DEBUG: Command ADMIN executed"
		level = level.rstrip("\n")
		playernumber, playername = searchplayer(partialname)
		if playername:
			guid = searchguid(playernumber) #Solicitamos su GUID
			if level == "admin": dbcursor.execute("UPDATE Players SET Level=10 WHERE Guid=?",(guid,))
			elif level == "moderador": dbcursor.execute("UPDATE Players SET Level=5 WHERE Guid=?",(guid,))
			elif level == "regular": dbcursor.execute("UPDATE Players SET Level=0 WHERE Guid=?",(guid,))
			else:
				send_rcon("%s Por favor indique bien el nivel (admin, moderador o regular)" %BOT)
				return False
			dbconnection.commit() #Le modificamos el Level en la DB.
			send_rcon("%s Poderes cambiados a: ^2%s (%s)" %(BOT,playername,level)) #Notificamos el hecho
			print "[Pantufla]: %s PODERES CAMBIADOS!" %playername
			return True #Salimos.
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command ADMIN rejected, no admin"

## Permite buscar aliases de los players en la DB
def cmd_alias(caller, partialname):
	if check_admin(caller) >= LVL_ALIAS:
		print "DEBUG: Command ALIAS executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			if playername is not "ID":
				guid = searchguid(playernumber) #Solicitamos su GUID
				dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (guid,)) #Pedimos la info de esa GUID
				row = dbcursor.fetchone()
				playernumber = row[0]
			dbcursor.execute("SELECT * FROM Aliases WHERE ID=?", (playernumber,)) #La lista de aliases para ese ID.
			rows = dbcursor.fetchall()
			send_rcon("%s Aliases de %s:" %(BOT,playername))
			for rowaliases in rows: send_rcon("%s %s" %(BOT,rowaliases[1])) #Los tiramos uno por renglon.
			return True
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command ALIAS rejected, no admin"

## Comando para forzar un jugador hacia otro equipo o a espectadores.
def cmd_force(caller, partialname, team):
	if check_admin(caller) >= LVL_FORCE:
		print "DEBUG: Command FORCE executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			team = team.rstrip("\n")
			if team == "rojo":
				send_rcon("forceteam %s red" %playernumber)
				send_rcon("%s Jugador ^2%s forzado al equipo ^1ROJO." %(BOT, playername))
			elif team == "azul":
				send_rcon("forceteam %s blue" %playernumber)
				send_rcon("%s Jugador ^2%s forzado al equipo ^4AZUL." %(BOT, playername))
			elif team == "spec":
				send_rcon("forceteam %s spectator" %playernumber)
				send_rcon("%s Jugador ^2%s forzado como ^2espectador." %(BOT, playername))
			else:
				send_rcon("%s Por favor indicar a donde mover al jugador: ^1rojo^7, ^4azul ^7o spec." %BOT)
				return False
			return True
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command FORCE rejected, no admin"

## Para averiguar el @ID del PlayerName en la DB.
def cmd_id(caller, partialname):
	if check_admin(caller) >= LVL_ID:
		print "DEBUG: Command ID executed"
		partialname = "%"+partialname.rstrip("\n")+"%" #Formateo para SQLite3.
		dbcursor.execute("SELECT * FROM Players WHERE Name LIKE ?", (partialname,))
		rows = dbcursor.fetchall() #Buscamos nombres similares a partialname.
		dbcursor.execute("SELECT * FROM Aliases WHERE ALIAS LIKE ?", (partialname,))
		aliasrows = dbcursor.fetchall() #Buscamos aliases similares a partialname.
		if not rows and not aliasrows: send_rcon("%s No hay IDs para ese nombre." %BOT)
		else:
			send_rcon("%s IDs encontrados:" %BOT)
			#if rows: #Si encontramos la ID en los nombres, mostrar.
				#for ids in rows: send_rcon("%s ^2@%s^7: %s" %(BOT,ids[0],ids[1]))
			if aliasrows: #Si encontramos la ID en los aliases, mostrar.
				for ids in aliasrows: send_rcon("%s ^2@%s^7: %s" %(BOT,ids[0],ids[1]))
			return True
		return False
	else: print "DEBUG: Command ID rejected, no admin"

## Para recargar la config y reiniciar el servidor.
def cmd_recargar(caller):
	if check_admin(caller) >= LVL_RECARGAR:
		print "DEBUG: Command RECARGAR executed"
		send_rcon("%s Reiniciando el servidor..." %BOT)
		send_rcon("reload")
	else: print "DEBUG: Command RECARGAR rejected, no admin"

## Para reiniciar la partida solamente.
def cmd_reiniciar(caller):
	if check_admin(caller) >= LVL_REINICIAR:
		print "DEBUG: Command REINICIAR executed"
		send_rcon("%s Reiniciando el mapa actual." %BOT)
		send_rcon("restart")
	else: print "DEBUG: Command REINICIAR rejected, no admin"

## Comando para equilibrar equipos (eligiendo uno al azar).
def cmd_teams(caller):
	if check_admin(caller) >= LVL_TEAMS:
		print "DEBUG: Command TEAMS executed"
		# La cvar "g_xTeamList" devuelve "ABC..Xn" donde cada letra corresponde a un PlayerNumber.
		rteamlist = send_rcon("g_redTeamList").split('"') #Buscamos la lista de players.
		bteamlist = send_rcon("g_blueTeamList").split('"')
		teamdiff = len(rteamlist[3]) - len(bteamlist[3]) #Sacamos la diferencia.
		if teamdiff >= 2:
			send_rcon("%s Equilibrando equipos..." %BOT)
			rteamlist = rteamlist[3][:2]
			playerselectd = ord(choice(rteamlist))-65 #Convertimos la letra a un int.
			send_rcon("forceteam %s blue" %playerselectd) #Forzamos y chau.
			return True
		elif teamdiff <= -2:
			send_rcon("%s Equilibrando equipos..." %BOT)
			bteamlist = bteamlist[3][:2]
			playerselectd = ord(choice(bteamlist))-65
			send_rcon("forceteam %s red" %playerselectd)
			return True
		else: #Si hay una diferencia menor o igual a 1 jugador.
			send_rcon("%s Los equipos ya estan equilibrados (en cantidad)." %BOT)
			return False
	else: print "DEBUG: Command TEAMS rejected, no admin"	

## Comando para expulsar a un PlayerName.
def cmd_kick(caller, partialname):
	if check_admin(caller) >= LVL_KICK:
		print "DEBUG: Command KICK executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("kick %s" %playernumber) #Kickea al playernumber.
			print "Debug: %s KICKED!" %playername
	else: print "DEBUG: Command KICK rejected, no admin"

## Comando para bannear a un PlayerName o @ID.
def cmd_ban(caller, partialname, reason):
	if check_admin(caller) >= LVL_BAN:
		print "DEBUG: Command BAN executed"
		reason = reason.rstrip("\n")
		playernumber, playername = searchplayer(partialname)
		if playername:
			if playername is not "ID": #Iniciamos la busqueda del Guid en caso que se banee un nombre.
				dbcursor.execute("SELECT * FROM Players WHERE Guid=?", (searchguid(playernumber),)) #Pedimos la info de esa GUID
				row = dbcursor.fetchone()
				send_rcon("kick %s" %playernumber) #Kickea al playernumber.
				playernumber = row[0]
			dbcursor.execute("INSERT INTO Bans VALUES(?,?,0,?)",(playernumber,time.time(),reason))
			dbconnection.commit() #Sino, simplemente banneamos por @ID.
			send_rcon("%s Banneando a: %s (Razon: %s)" %(BOT,playername,reason))
			print "Debug: %s BANNED!" %playername
	else: print "DEBUG: Command BAN rejected, no admin"

## Comando para quitarle el ban a un @ID.
def cmd_unban(caller, id):
	if check_admin(caller) >= LVL_UNBAN:
		if id[:1] == "@": #Asegurarse que quiera desbannear un @ID.
			id = int(id[1:])
			print "DEBUG: Command DESBAN executed"
			dbcursor.execute("DELETE FROM Bans WHERE Id=?", (id,))
			dbconnection.commit() #Mandamos a borrar el ban sin chequear.
			send_rcon("%s ID %s desbanneado correctamente." %(BOT,id))
			return True
		else:
			send_rcon("%s ID invalida para quitar el ban." %BOT)
			return False
	else: print "DEBUG: Command UNBAN rejected, no admin"

## Comando para slappear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_slap(caller, partialname):
	if check_admin(caller) >= LVL_SLAP:
		print "DEBUG: Command SLAP executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("slap %s" %playernumber) #Slapea al playernumber.
			print "Debug: %s SLAPPED!" %playername
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command SLAP rejected, no admin"

## Comando para nukear a alguien (SIEMPRE ABUSAN DE ESTO).
def cmd_nuke(caller, partialname):
	if check_admin(caller) >= LVL_NUKE:
		print "DEBUG: Command NUKE executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("nuke %s" %playernumber) #Nuke al playernumber.
			print "Debug: %s NUKED!" %playername
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command NUKE rejected, no admin"

## Comando para mutear a alguien.
def cmd_mute(caller, partialname):
	if check_admin(caller) >= LVL_MUTE:
		print "DEBUG: Command MUTE executed"
		playernumber, playername = searchplayer(partialname)
		if playername:
			send_rcon("mute %s" %playernumber) #Nuke al playernumber.
			print "Debug: %s MUTED!" %playername
			return True
		else:
			send_rcon("%s No hay ningun jugador con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command MUTE rejected, no admin"

## Comando para cambiar el mapa instantaneamente.
def cmd_map(caller, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(caller) >= LVL_MAP:
		print "DEBUG: Command MAP executed"
		mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
		with open(CYCLEMAP, 'r') as fmap: availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
		fmap.close()
		for x in range(len(availablemaps)):
			if mapname in availablemaps[x]:
				send_rcon("%s Cambiando el mapa a %s" %(BOT,availablemaps[x]))
				time.sleep(1)
				send_rcon("map %s" %availablemaps[x]) #Si el mapa esta en el cycle, cambiar.
				return True
		send_rcon("%s No encuentro ningun mapa con ese nombre." %BOT)
		return False
	else: print "DEBUG: Command MAP rejected, no admin"

## Comando para ver y cambiar el mapa siguiente.
def cmd_nextmap(caller, mapname): #True = Mapa cambiado; False = NO.
	if check_admin(caller) >= LVL_NEXTMAP:
		print "DEBUG: Command NEXTMAP executed"
		with open(CONFIG["CYCLEMAP"], 'r') as fmap: availablemaps = fmap.read().splitlines() #Abrimos el cycle y armamos la lista.
		fmap.close()
		if mapname == None:
			buffer = send_rcon("g_nextmap").split('"') #Vemos si el nextmap ya se cambio.
			if buffer[3] == "^7": #Si el nextmap no se cambio, calcularlo.
				buffer = send_rcon("status").split("\n")
				buffer = buffer[1].split()
				for x in range(len(availablemaps)):
					if buffer[1] in availablemaps[x]:
						send_rcon("%s El mapa siguiente es: ^2%s" %(BOT,availablemaps[x+1]))
						return True
				return False
			else: #Si el nextmap se cambio, mostrar a cual.
				send_rcon("%s El mapa siguiente es: ^2%s" %(BOT,buffer[3]))
				return True
		else:
			mapname = mapname.rstrip("\n") #El comando probablemente venga con \n.
			for x in range(len(availablemaps)):
				if mapname in availablemaps[x]:
					send_rcon("%s Cambiando el mapa SIGUIENTE a ^2%s" %(BOT,availablemaps[x]))
					send_rcon("g_nextmap %s" %availablemaps[x]) #Si el mapa esta en el cycle, cambiar.
					return True
			send_rcon("%s No encuentro ningun mapa con ese nombre." %BOT)
			return False
	else: print "DEBUG: Command NEXTMAP rejected, no admin"

## Comando para iniciar el matchmode:
def cmd_matchmode(caller, mode): #True = Listo para empezar; False = Error.
	if check_admin(caller) >= LVL_CERRADO:
		print "DEBUG: Command CERRADO executed" #Va con argumento (TS, CTF, etc...)
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon("%s Cerrando el server para un partido de TS..." %BOT)
			send_rcon("%s Reglas del juego cargadas: ^2UrTLA TS" %BOT)
			send_rcon("exec %s" %CONFIG["MATCHTS"])
			time.sleep(3) #Hacemos tiempo porque los players son luisitos.
			send_rcon("%s Por favor, elegir un mapa para empezar." %BOT)
			return True
		elif mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon("%s Cerrando el server para un partido de CTF..." %BOT)
			send_rcon("%s Reglas del juego cargadas: ^2UrTLA CTF" %BOT)
			send_rcon("exec %s" %CONFIG["MATCHCTF"])
			time.sleep(3) #Hacemos tiempo porque los players son luisitos.
			send_rcon("%s Por favor, elegir un mapa para empezar." %BOT)
			return True
		send_rcon("%s No tengo disponible ese modo de juego." %BOT)
		return False
	else: print "DEBUG: Command CERRADO rejected, no admin"

## Comando para hacer publico el server:
def cmd_publicmode(caller, mode): #True = Listo para empezar; False = Error.
	if check_admin(caller) >= LVL_PUBLICO:
		print "DEBUG: Command PUBLICO executed" #Va con argumento (TS, CTF, etc...)
		if mode.rstrip("\n") == "ts": #El comando probablemente venga con \n.
			send_rcon("%s Configurando el server en modo ^2PUBLICO TS^7." %BOT)
			time.sleep(1)
			send_rcon("exec %s" %CONFIG["PUBLICTS"])
			return True
		elif mode.rstrip("\n") == "ctf": #El comando probablemente venga con \n.
			send_rcon("%s Abriendo el server en modo ^2PUBLICO CTF^7." %BOT)
			time.sleep(1)
			send_rcon("exec %s" %CONFIG["PUBLICCTF"])
			return True
		send_rcon("%s No tengo disponible ese modo de juego." %BOT)
		return False
	else: print "DEBUG: Command PUBLICO rejected, no admin"
	
## Principal:
if __name__ == "__main__":
	try: # Inicializacion de la DB
		dbconnection = lite.connect("Pantufla.db")
		dbconnection.text_factory = str
		dbcursor = dbconnection.cursor()
		dbcursor.execute("CREATE TABLE IF NOT EXISTS Players(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Guid TEXT, Level INT)")
		dbcursor.execute("CREATE TABLE IF NOT EXISTS Aliases(ID INT, ALIAS TEXT)")
		dbcursor.execute("CREATE TABLE IF NOT EXISTS Bans(ID INT, Date FLOAT, Until FLOAT, Reason TEXT)")
	except lite.Error, e:
		print "ERROR %s: Problema con la base de datos." %e.args[0]
		sys.exit(1)

	# Cargamos el archivo de config.
	CONFIG ={}
	try:
		execfile(FCONFIG, CONFIG)
		HOST = CONFIG["HOST"]
		PORT = CONFIG["PORT"]
		RCONPWD = CONFIG["PASSWORD"]
		LVL_ALIAS = CONFIG["LVL_ALIAS"]
		LVL_FORCE = CONFIG["LVL_FORCE"]
		LVL_ID = CONFIG["LVL_ID"]
		LVL_RECARGAR = CONFIG["LVL_RECARGAR"]
		LVL_REINICIAR = CONFIG["LVL_REINICIAR"]
		LVL_TEAMS = CONFIG["LVL_TEAMS"]
		LVL_KICK = CONFIG["LVL_KICK"]
		LVL_BAN = CONFIG["LVL_BAN"]
		LVL_UNBAN = CONFIG["LVL_UNBAN"]
		LVL_SLAP = CONFIG["LVL_SLAP"]
		LVL_NUKE = CONFIG["LVL_NUKE"]
		LVL_MUTE = CONFIG["LVL_MUTE"]
		LVL_MAP = CONFIG["LVL_MAP"]
		LVL_NEXTMAP = CONFIG["LVL_NEXTMAP"]
		LVL_CERRADO = CONFIG["LVL_CERRADO"]
		LVL_PUBLICO = CONFIG["LVL_PUBLICO"]
	except:
		print "ERROR: Falla al abrir el archivo de configuracion."
		sys.exit(1)
	print "[Pantufla]: Inicializando programa... OK."

	# Inicializacion del socket y mandamos nuestros primeros mensajes.
	send_rcon(VERMSG)
	print "[Pantufla]: Enviando bienvenida... OK."

	# Abrimos el log del server de urt y buscamos el EOF
	fp = open(CONFIG["SERVERLOG"], 'r')
	while True:
		new = fp.readline()
		if not new: break
	print "[Pantufla]: Log cargado, listo para parsear ordenes..."

	# Recibimos lineas nuevas en tiempo real de mentira y las parseamos.
	while True:
		new = fp.readline()
		if new: parser_cmd(new)
		time.sleep(0.01)
	
	# Si de alguna manera se llega a este lugar, salir limpio.
	fp.close()
	print "[Pantufla]: Saliendo..."
