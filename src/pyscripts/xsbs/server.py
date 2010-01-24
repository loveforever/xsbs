from xsbs.players import masterRequired, player
from xsbs.events import eventHandler
from xsbs.commands import commandHandler
from xsbs.ui import notice
from xsbs.settings import PluginConfig

import string
import sbserver

config = PluginConfig('server')
pause_message = config.getOption('Templates', 'pause_message', 'The game has been ${action} by ${orange}${name}')
del config
pause_message = string.Template(pause_message)

def isPaused():
	'''Is the game currently paused'''
	return sbserver.isPaused()

def setPaused(val, cn=-1):
	'''Pause or unpause the game'''
	if val == isPaused():
		return
	if val:
		action = 'paused'
	else:
		action = 'unpaused'
	try:
		p = player(cn)
	except ValueError:
		name = 'Unknown'
	else:
		name = p.name()
	sbserver.message(notice(pause_message.substitute(
		colordict,
		action=action,
		name=name)))
	sbserver.setPaused(val)

def adminPassword():
	'''Administrator password of server.'''
	return sbserver.adminPassword()

def ip():
	'''Ip address server is bound to.'''
	return sbserver.ip()

def port():
	'''Port server is bound to.'''
	return sbserver.port()

def reload():
	'''Reload python system.'''
	return sbserver.reload()

def setBotLimit(limit):
	'''Set maximum number of bots.'''
	return sbserver.setBotLimit(limit)

def uptime():
	'''Server uptime in miliseconds.'''
	return sbserver.uptime()

def message(string):
	'''Send message to server.'''
	sbserver.message(string)

def setMasterMode(mm_number):
	'''Set server master mode.
	   0 - open
	   1 - veto
	   2 - locked
	   3 - private'''
	sbserver.setMasterMode(mm_number)

def maxClients():
	'''Maximum clients allowed in server.'''
	return sbserver.maxClients()

def setMaxClients(num_clients):
	'''Set the maximum clients allowed in server.'''
	return sbserver.setMaxClients(number)

@eventHandler('player_pause')
@masterRequired
def onPlayerPause(cn, val):
	setPaused(val, cn)

