import sbserver
from xsbs.events import triggerServerEvent
from xsbs.commands import commandHandler, UsageError
from xsbs.settings import PluginConfig
from xsbs.colors import red, yellow, blue, green, colordict
from xsbs.plugins import reload as pluginReload
from xsbs.ui import error, info, insufficientPermissions
from xsbs.net import ipLongToString
from Motd.motd import motdstring
from UserPrivilege.userpriv import masterRequired, adminRequired
import string

config = PluginConfig('servercommands')
servermsg_template = config.getOption('Templates', 'servermsg', '${orange}${sender}${white}: ${message}')
del config
servermsg_template = string.Template(servermsg_template)

@commandHandler('pause')
@masterRequired
def onPauseCmd(cn, args):
	'''@description Pause the game
	   @usage'''
	if args != '':
		raise UsageError('')
		return
	sbserver.setPaused(True)

@commandHandler('resume')
@masterRequired
def onResumeCmd(cn, args):
	'''@description Resume game from pause
	   @usage'''
	if args != '':
		raise UsageError('')
		return
	sbserver.setPaused(False)

@commandHandler('reload')
@adminRequired
def onReloadCmd(cn, args):
	'''@description Reload server plugins
	   @usage'''
	if args != '':
		raise UsageError('')
	else:
		sbserver.playerMessage(cn, yellow('NOTICE: ') + blue('Reloading server plugins.  Fasten your seatbelts...'))
		pluginReload()

@commandHandler('givemaster')
@masterRequired
def onGiveMaster(cn, args):
	'''@description Give master to a client
	   @usage cn'''
	if args == '':
		raise UsageError('cn')
		return
	try:
		tcn = int(args)
	except TypeError:
		raise UsageError('cn')
		return
	sbserver.playerMessage(cn, info('You have given master to %s') % sbserver.playerName(tcn))
	sbserver.setMaster(tcn)

@commandHandler('resize')
@adminRequired
def onResize(cn, args):
	'''@description Change maximum clients allowed in server
	   @usage maxclients'''
	if args == '':
		raise UsageError('maxclients')
	else:
		size = int(args)
		sbserver.setMaxClients(int(args))

@commandHandler('minsleft')
@masterRequired
def onMinsLeft(cn, args):
	'''@description Set minutes left in current match
	   @usage minutes'''
	if args == '':
		raise UsageError('minutes')
	else:
		sbserver.setMinsRemaining(int(args))

@commandHandler('specall')
@masterRequired
def specAll(cn, args):
	'''@description Make all clients spectators
	   @usage'''
	if args != '':
		raise UsageError('')
	else:
		for s in sbserver.players():
			sbserver.spectate(s)

@commandHandler('unspecall')
@masterRequired
def unspecAll(cn, args):
	'''@description Make all clients players
	   @usage'''
	if args != '':
		raise UsageError('')
	else:
		for s in sbserver.spectators():
			sbserver.unspectate(s)

@commandHandler('servermsg')
@masterRequired
def serverMessage(cn, args):
	'''@description Broadcast message to all clients in server
	   @usage message'''
	if args == '':
		raise UsageError('message')
	else:
		msg = servermsg_template.substitute(colordict, sender=sbserver.playerName(cn), message=args)
		sbserver.message(msg)

@commandHandler('ip')
@masterRequired
def playerIp(cn, args):
	'''@description Get string representation of client ip
	   @usage cn'''
	if args == '':
		raise UsageError('cn')
	else:
		sbserver.message(info(player(int(args)).ipString()))

