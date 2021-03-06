import sbserver
from xsbs.colors import colordict
from xsbs.ui import notice
from xsbs.server import isFrozen
from xsbs.commands import StateError
import string

modes = [
	'ffa',
	'coop',
	'team',
	'insta',
	'instateam',
	'effic',
	'efficteam',
	'tac',
	'tacteam',
	'capture',
	'regencapture',
	'ctf',
	'instactf',
	'protect',
	'instaprotect'
]

def modeName(modenum):
	'''String representing game mode number'''
	return modes[modenum]

def modeNumber(modename):
	'''Number representing game mode string'''
	i = 0
	for mode in modes:
		if modename == mode:
			return i
		i += 1
	raise ValueError('Invalid mode')

def currentMap():
	'''Name of current map'''
	return sbserver.mapName()

def currentMode():
	'''Integer value of current game mode'''
	return sbserver.gameMode()

def setMap(map_name, mode_number):
	'''Set current map and mode'''
	if isFrozen():
		raise StateError('Server is currently frozen')
	sbserver.setMap(map_name, mode_number)

