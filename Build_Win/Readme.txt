PantuflaBot
===========

Un simple bot administrativo para Urban Terror 4.1 (no está testeado en la 4.2)

Escrito en Python 2.7, lee constantemente los logs del juego y almacena datos basicos en SQLite3.

Los comandos que posee son:

Comando	Descripción
!pantufla	Responde un mensaje si el player es administrador.
!admin [PLAYER]	Le da permisos de admin al PLAYER mencionado.
!alias [PLAYER]	Devuelve los aliases del PLAYER mencionado.
!recargar	Recarga la configuración y reinicia el servidor.
!reiniciar	Reinicia la partida instantaneamente, no recarga la configuración.
!kick [PLAYER]	Echa a un jugador de la partida.
!slap [PLAYER]	Castiga a un jugador de la partida.
!nuke [PLAYER]	Intenta matar a un jugador de la partida.
!map [MAPA]	Cambia el mapa de juego instantaneamente.
!nextmap [MAPA]	Cambia el mapa de la siguiente ronda del juego.
!cerrado [MODO]	Cierra el servidor y lo prepara con el modo de juego especificado.
!publico [MODO]	Abre el servidor (publico) y/o cambia el modo de juego (si ya esta abierto).

El bot se encuentra en constante desarrollo, requiere una configuración un poco descuidada, y seguramente tenga bugs. Usar bajo propia responsabilidad.

El código se encuentra comentado y es bastante fácil de leer, puede servir para entender el protocolo de rcon (Urban Terror, Q3, etc...) y realizar otros proyectos.
