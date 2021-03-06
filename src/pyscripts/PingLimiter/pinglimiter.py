import sbserver
from xsbs.timers import addTimer
from xsbs.ban import ban
from xsbs.settings import PluginConfig
from xsbs.ui import warning, notice
from xsbs.commands import commandHandler, UsageError
from xsbs import players
from xsbs.players import adminRequired

config = PluginConfig('pinglimiter')
enable = config.getOption('Config', 'enable', 'yes') == 'yes'
max_ping = config.getOption('Config', 'max_ping', '500')
action_interval = config.getOption('Config', 'action_interval', '5')
del config
max_ping = int(max_ping)
action_interval = int(action_interval)

class PingLimiter:
	def __init__(self, max_ping, action_interval):
		self.max_ping = max_ping
		self.action_interval = action_interval
		self.counter = action_interval
		self.warned_cns = []
		self.enabled = True
	def checkPlayers(self):
		addTimer(5000, self.checkPlayers, ())
		if not self.enabled:
			return
		self.update_averages()
		if self.counter == 0:
			laggers = []
			for player in players.all():
				try:
					if not player.isSpectator() and player.avg_ping > self.max_ping:
						laggers.append(player.cn)
				except AttributeError:
					player.avg_ping = 0
			remove_cns = []
			for lagger in laggers:
				if lagger in self.warned_cns:
					ban(lagger, 0, 'lagging', -1)
					remove_cns.append(lagger)
				else:
					sbserver.playerMessage(lagger, warning('Your ping is too high.  You will be kicked if it is not lowered.'))
					self.warned_cns.append(lagger)
			for r_cns in remove_cns:
				self.warned_cns.remove(r_cns)
	def update_averages(self):
		"""
		Uses an exponential average, this will punish spikes harder than a multiple of instances calculated into an average.
		A spike-friendlier method is to arrange a list of values and calculate the average on the whole list divided by its length,
		like this: sum(pingvalueslist)/len(pingvalueslist) //Henrik L
		"""
		for player in players.all():
			try:
				player.avg_ping = (player.avg_ping + player.ping()) / 2
			except AttributeError:
				player.avg_ping = player.ping() / 2
		if self.counter:
			self.counter -= 1
		else:
			self.counter = self.action_interval

limiter = PingLimiter(max_ping, action_interval)
limiter.enabled = enable
addTimer(5000, limiter.checkPlayers, ())

@commandHandler('pinglimiter')
@adminRequired
def pingLimiterCmd(cn, args):
	'''@description Enable or disable kicking high ping users
	   @usage enable/disable'''
	if args == 'enable':
		limiter.enabled = True
		sbserver.playerMessage(cn, notice('Ping limiter enabled'))
	elif args == 'disable':
		limiter.enabled = False
		sbserver.playerMessage(cn, notice('Ping limiter disabled'))
	else:
		raise UsageError('enable/disable')

