from elixir import Entity, Field, String, Integer, ManyToOne, OneToMany, setup_all, session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from xsbs.events import eventHandler, policyHandler, triggerServerEvent, registerServerEventHandler, registerPolicyEventHandler
from xsbs.commands import commandHandler, UsageError, StateError, ArgumentValueError
from xsbs.colors import red, green, orange
from xsbs.ui import info, error, warning
from xsbs.settings import loadPluginConfig
from xsbs.ban import ban
from xsbs.timers import addTimer

import sbserver
import re

config = {
	'Main': {
		'blocked_reserved_names': 'unnamed, admin',
		}
	}

loadPluginConfig(config, 'UserManager')
config['Main']['blocked_reserved_names'] = config['Main']['blocked_reserved_names'].strip(' ').split(',')

class NickAccount(Entity):
	nick = Field(String(15))
	user = ManyToOne('User')
	def __init__(self, nick, user):
		self.nick = nick
		self.user = user

class Group(Entity):
	name = Field(String(30))
	users = OneToMany('User')
	def __init__(self, name):
		self.name = name

class User(Entity):
	email = Field(String(50))
	password = Field(String(20))
	privilege = Field(Integer)
	nickaccounts = OneToMany('NickAccount')
	groups = ManyToOne('Group')
	def __init__(self, email, password, privilege=0):
		self.email = email
		self.password = password
		self.privilege = privilege

def userFromId(user_id):
	user = User.query.filter(id==User.id).one()
	return user

def isUserIdMaster(user_id):
	user = userFromId(user_id)
	return user.privilege >= 1

def isUserIdAdmin(user_id):
	user = userFromId(user_id)
	return user.privilege == 2

def userAuth(email, password):
	try:
		user = User.query.filter(User.email==email).filter(User.password==password).one()
	except (NoResultFound, MultipleResultsFound):
		return False
	return user

def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

@eventHandler('player_setmaster')
def onSetMaster(cn, givenhash):
	p = player(cn)
	adminhash = sbserver.hashPassword(cn, sbserver.adminPassword())
	try:
		na = NickAccount.query.filter(NickAccount.nick==p.name()).one()
	except NoResultFound:
		if givenhash != adminhash:
			setSimpleMaster(cn)
	except MultipleResultsFound:
		p.message(error(' This name is linked to multiple accounts.  Contact the system administrator.'))
	else:
		nickhash = sbserver.hashPassword(cn, na.user.password)
		if givenhash == nickhash:
			login(cn, na.user)
		else:
			if givenhash != adminhash:
				setSimpleMaster(cn)

def setSimpleMaster(cn):
	p = player(cn)
	if sbserver.publicServer() == 1:
		sbserver.playerMessage(cn, error('This is not an open server, you need auth or master privileges to get master.'))
		return
	if currentAdmin() != None:
		sbserver.playerMessage(cn, error('Admin is present'))
		return
	if currentMaster() != None:
		sbserver.playerMessage(cn, error('Master is present'))
		return
	sbserver.setMaster(cn)

def warnNickReserved(cn, count, sessid):
	try:
		p = player(cn)
	except ValueError:
		return
	try:
		nickacct = p.warn_nickacct
		if nickacct.nick != sbserver.playerName(cn) or sessid != sbserver.playerSessionId(cn):
			p.warning_for_login = False
			return
	except (AttributeError, ValueError):
		p.warning_for_login = False
		return
	if isLoggedIn(cn):
		user = loggedInAs(cn)
		if nickacct.user_id != user.id:
			ban(cn, 0, 'Use of reserved name', -1)
		p.warning_for_login = False
		return
	if count > 4:
		ban(cn, 0, 'Use of reserved name', -1)
		p.warning_for_login = False
		return
	remaining = 25-(count*5)
	sbserver.playerMessage(cn, warning('Your name is reserved. You have ' + red('%i') + ' seconds to login or be kicked.') % remaining)
	addTimer(5000, warnNickReserved, (cn, count+1, sessid))

def nickReserver(nick):
	return NickAccount.query.filter(NickAccount.nick==nick).one()

@eventHandler('player_connect')
def onPlayerActive(cn):
	nick = sbserver.playerName(cn)
	p = player(cn)
	try:
		nickacct = nickReserver(sbserver.playerName(cn))
	except NoResultFound:
		p.warning_for_login = False
		return
	p = player(cn)
	p.warning_for_login = True
	p.warn_nickacct = nickacct
	warnNickReserved(cn, 0, sbserver.playerSessionId(cn))
	
@policyHandler('connect_with_pass')
def connectWithPass(cn, args):
	p = player(cn)
	adminhash = sbserver.hashPassword(cn, sbserver.adminPassword())
	try:
		na = NickAccount.query.filter(NickAccount.nick==p.name()).one()
	except NoResultFound:
		return False
	except MultipleResultsFound:
		p.message(error('Multiple names linked to this account.  Contact the system administrator.'))
		return False
	else:
		nickhash = sbserver.hashPassword(cn, na.user.password)
		if args == nickhash:
			login(cn, na.user)
			user_id = p.user.id
			if isUserMaster(user_id):
				return True
		else:
			return False

@eventHandler('player_name_changed')
def onPlayerNameChanged(cn, old_name, new_name):
	onPlayerActive(cn)

