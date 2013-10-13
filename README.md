PantuflaBot
===========

Un simple bot administrativo para Urban Terror 4.1 (no está testeado en la 4.2)

Escrito en Python 2.7, lee constantemente los logs del juego y almacena datos basicos en SQLite3.

Los comandos que posee son:
<table>
	<thead><tr><th>Comando</th><th>Descripción</th></tr></thead>
	<tbody>
		<tr>
		<td>!pantufla</td>
		<td>Responde un mensaje si el player es administrador.</td>
		</tr>
		<tr>
		<td>!admin [PLAYER]</td>
		<td>Le da permisos de admin al PLAYER mencionado.</td>
		</tr>
		<tr>
		<td>!alias [PLAYER]</td>
		<td>Devuelve los aliases del PLAYER mencionado.</td>
		</tr>
		<tr>
		<td>!recargar</td>
		<td>Recarga la configuración y reinicia el servidor.</td>
		</tr>
		<tr>
		<td>!reiniciar</td>
		<td>Reinicia la partida instantaneamente, no recarga la configuración.</td>
		</tr>
		<tr>
		<td>!kick [PLAYER]</td>
		<td>Echa a un jugador de la partida.</td>
		</tr>
		<tr>
		<td>!slap [PLAYER]</td>
		<td>Castiga a un jugador de la partida.</td>
		</tr>
		<tr>
		<td>!nuke [PLAYER]</td>
		<td>Intenta matar a un jugador de la partida.</td>
		</tr>
		<tr>
		<td>!map [MAPA]</td>
		<td>Cambia el mapa de juego instantaneamente.</td>
		</tr>
		<tr>
		<td>!nextmap [MAPA]</td>
		<td>Cambia el mapa de la siguiente ronda del juego.</td>
		</tr>
		<tr>
		<td>!cerrado [MODO]</td>
		<td>Cierra el servidor y lo prepara con el modo de juego especificado.</td>
		</tr>
		<tr>
		<td>!publico [MODO]</td>
		<td>Abre el servidor (publico) y/o cambia el modo de juego (si ya esta abierto).</td>
		</tr>
	</tbody>
</table>

El bot se encuentra en constante desarrollo, requiere una configuración un poco descuidada, y seguramente tenga bugs. Usar bajo propia responsabilidad.

El código se encuentra comentado y es bastante fácil de leer, puede servir para entender el protocolo de rcon (Urban Terror, Q3, etc...) y realizar otros proyectos.
