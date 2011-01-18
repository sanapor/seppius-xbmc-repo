# (c) Eugene Bond
# eugene.bond@gmail.com
#
# kartina tv XML/json api

import urllib2
import demjson

from time import time
import datetime

import re, os, sys

__author__ = 'Eugene Bond <eugene.bond@gmail.com>'
__version__ = '2.5'

try:
	import xbmc, xbmcaddon
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
		
		def output(self, data):
			print data
		
		def getInfoLabel(self, param):
			return '%s unknown' % param
	
	class xbmcaddon_foo:
		def __init__(self, id):
			self.id = id
		
		def getAddonInfo(self, param):
			if param == 'version':
				return __version__
			elif param == 'id':
				return self.id + ' by %s' % __author__
			else:
				return '%s unknown' % param
	
	class xbmcaddon_boo:
		def Addon(self, id = ''):
			if not id:
				id = os.path.basename(__file__)
			return xbmcaddon_foo(id)
	
	xbmc = xbmc_boo()
	xbmcaddon = xbmcaddon_boo()


#
# platform package usage disabled as
# cousing problems with x64 platforms
#
#try:
#	import platform
#except ImportError:
class platform_boo:
	
	def system(self):
		return os.name
	
	def release(self):
		plat = sys.platform
		return plat
			
	def python_version(self):
		ver = sys.version_info
		return '%s.%s.%s' % (ver[0], ver[1], ver[2])

platform = platform_boo()


KARTINA_API = 'http://iptv.kartina.tv/api/json/%s'


class kartina:
	
	def __init__(self, login, password, addonid = '', SID = None, SID_NAME = None):
		self.SID = SID
		self.SID_NAME = SID_NAME
		self.channels = []
		self.channels_ttl = 0
		self.login = login
		self.password = password
		self.addonid = addonid
		self.timeshift = None
		#, 
		self.supported_settings = {'stream_server': {'name': 'stream_server', 'language_key': 34001, 'lookup': 'ip', 'display': 'descr'}, 'timeshift': {'name': 'timeshift', 'language_key': 34002}, 'bitrate': {'name': 'bitrate', 'language_key': 34004}, 'timezone': {'name': 'timezone', 'language_key': 34003, 'defined': [('-12', '-12 GMT (New Zealand Standard Time)'), ('-11', '-11 GMT (Midway Islands Time)'), ('-10', '-10 GMT (Hawaii Standard Time)'), ('-9', '-9 GMT (Alaska Standard Time)'), ('-8', '-8 GMT (Pacific Standard Time)'), ('-7', '-7 GMT (Mountain Standard Time)'), ('-6', '-6 GMT (Central Standard Time)'), ('-5', '-5 GMT (Eastern Standard Time)'), ('-4', '-4 GMT (Puerto Rico and US Virgin Islands Time)'), ('-3', '-3 GMT (Argentina Standard Time)'), ('-2', '-2 GMT'), ('-1', '-1 GMT (Central African Time)'), ('0', '0 GMT (Greenwich Mean Time)'), ('1', '+1 GMT (European Central Time)'), ('2', '+2 GMT (Eastern European Time)'), ('3', '+3 GMT (Eastern African Time)'), ('4', '+4 GMT (Near East Time)'), ('5', '+5 GMT (Pakistan Lahore Time)'), ('6', '+6 GMT (Bangladesh Standard Time)'), ('7', '+7 GMT (Vietnam Standard Time)'), ('8', '+8 GMT (China Taiwan Time)'), ('9', '+9 GMT (Japan Standard Time)'), ('10', '+10 GMT (Australia Eastern Time)'), ('11', '+11 GMT (Solomon Standard Time)')]}}
	
	def _request(self, cmd, params):
		
		if self.SID == None:
			if cmd != 'login':
				self._auth(self.login, self.password)
		
		url = KARTINA_API % cmd
		url = url + '?' + params
		
		#log.info('Requesting %s' % url)
		xbmc.output('[Kartina.TV] REQUESTING: %s' % url)
		
		osname = '%s %s' % (platform.system(), platform.release())
		pyver = platform.python_version()
		
		__settings__ = xbmcaddon.Addon(self.addonid)
		
		isXBMC = 'XBMC'
		if getattr(xbmc, "nonXBMC", None) is not None:
			isXBMC = 'nonXBMC'
		
		ua = '%s v%s (%s %s [%s]; %s; python %s) as %s' % (__settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'), isXBMC, xbmc.getInfoLabel('System.BuildVersion'), xbmc.getInfoLabel('System.ScreenMode'), osname, pyver, self.login)
		
		xbmc.output('[Kartina.TV] UA: %s' % ua)
		
		req = urllib2.Request(url, None, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest'})
		
		if (self.SID != None):
			req.add_header("Cookie", self.SID_NAME + "=" + self.SID + ";")
		
		rez = urllib2.urlopen(req).read()
		
		xbmc.output('[Kartina.TV] Got %s' % rez)
		
		try:
			res = demjson.decode(rez)
		except:
			xbmc.output('[Kartina.TV] Error.. :(')
			
		xbmc.output('[Kartina.TV] Got JSON: %s' % res)
		
		self._errors_check(res)
		
		return res
	
	def _auth(self, user, password):
		response = self._request('login', 'login=%s&pass=%s' % (user, password))
		
		if 'sid' in response:
			self.SID = response['sid']
			self.SID_NAME = response['sid_name']
			value, options = self.getSettingCurrent('timeshift')
			self.timeshift = int(value) * 3600
		
	
	def _errors_check(self, json):
		
		if 'message' in json:
			xbmc.output('[Kartina.TV] ERROR: %s' % json['message'])
			#xbmc.Notification('Error', json['message'], 3)
			self.SID = None
			
	
	
	def getChannelsList(self):
		if self.channels_ttl < time():
			jsonChannels = self._request('channel_list', '')
			self.channels = []
			
			for channelGroup in jsonChannels['groups']:
				for channel in channelGroup['channels']:
					programm = ""
					if 'epg_progname' in channel:
						programm = channel['epg_progname']
					programm += "\n"
					prog, desc = programm.split("\n", 1)
					
					channel2add = { 
							'title':	channel['name'],
							'id':		channel['id'],
							'icon':		'http://iptv.kartina.tv%s' % channel['icon'],
							'info':		desc,
							'subtitle':	prog,
							'is_video':	('is_video' in channel) and (channel['is_video']),
							'have_archive': ('have_archive' in channel) and channel['have_archive'],
							'have_epg':	('epg_start' in channel) and (channel['epg_start']),
							'is_protected': ('protected' in channel) and (channel['protected']),
							'source':	channel,
							'genre':	channelGroup['name']
						}
					self.channels.append(channel2add)
				
			self.channels_ttl = time() + 600
		
		return self.channels
	
	def getStreamUrl(self, id, gmt = None, code = None): 
		params = 'cid=%s' % id
		if gmt != None:
			params += '&gmt=%s' % gmt
		
		if code != None:
			params += '&protect_code=%s' % code
		
		response = self._request('get_url', params)
		url = response['url']
		
		url = re.sub('http/ts(.*?)\s(.*)', 'http\\1', url)
		
		return url

	def getEPG(self, id, day = None):
		if not day:
			day = datetime.date.today().strftime('%d%m%y')
			
		params = 'cid=%s&day=%s' % (id, day)
		result = self._request('epg', params)
		res = []
		for epg in result['epg']:
			xbmc.output('[Kartina.TV] EPG item: %s' % epg)
			programm = ""
			if 'progname' in epg:
				programm = epg['progname']
			programm += "\n"
			prog, desc = programm.split("\n", 1)
			
			res.append({ 
				'title':		prog,
				'time':			int(epg['ut_start']),	#  + self.timeshift
				'info':			desc,
				'is_video':		0,
				'source':		epg
			})

		return res
	
	def getCurrentInfo(self, chid):
		response = self._request('epg_next', 'cid=%s' % chid)
		res = []
		
		if 'epg' in response and response['epg'] != False:
			epg = response['epg'][0:2]
			for prg in epg:
				programm = ""
				if 'progname' in prg:
					programm = prg['progname']
				programm += "\n"
				prog, desc = programm.split("\n", 1)
				res.append({ 
					'title':		prog,
					'time':			prg['ts'],
					'info':			desc,
					'is_video':		0
				})
			
		return res
	
	def getVideoList(self, mode, page, pagesize=15, search={}):
		params = 'type=%s&nums=%s&page=%s' % (mode, pagesize, page)
		result = self._request('vod_list', params)
		res = []
		for vod in result['rows']:
			xbmc.output('[Kartina.TV] VOD item: %s' % vod)
			res.append({
				'title':		vod['name'],
				'info':			vod['description'],
				'is_video':		1,
				'id':			vod['id'],
				'icon':			'http://iptv.kartina.tv%s' % vod['poster'],
				'source':		vod
			})
			
		return res
	
	def getVideoInfo(self, id):
		params = 'id=%s' % id
		result = self._request('vod_info', params)
		
		return result['film']
	
	
	def getVideoUrl(self, id):
		params = 'fileid=%s' % id
		response = self._request('vod_geturl', params)
		url = response['url']
		
		url, junk = url.split(" ",1)
		
		return url
	
	def getSettingCurrent(self, setting_name):
		setting = self.supported_settings[setting_name]
		res = self._request('settings', 'var=%s' % setting['name'])
		server_setting = res['settings']
		
		oplist = []
		if 'defined' in setting:
			oplist = setting['defined']	
		elif 'list' in server_setting:
			for set in server_setting['list']:
				if 'lookup' in setting:
					oplist.append((str(set[setting['lookup']]), str(set[setting['display']])))
				else:
					oplist.append((str(set), str(set)))
			
		return (server_setting['value'], oplist)
	
	def setSettingCurrent(self, setting_name, setting_value):
		res = self._request('settings_set', 'var=%s&val=%s' % (setting_name, setting_value))
	
	def getSettingsList(self):
		
		res = []
		for set in self.supported_settings:
			setting = self.supported_settings[set]
			value, options = self.getSettingCurrent(set)
			res.append({
				'name':			setting['name'],
				'language_key':	setting['language_key'],
				'value':		value,
				'options':		options
			})
		xbmc.output('[Kartina.TV] settings: %s' % res)
		return res
	
	
	def test(self):
		print(self.getChannelsList())
		print(self.getCurrentInfo(7))
	
	
	def testAuth(self):
		if self.SID:
			account = self._request('account', '')
		if self.SID == None:
			self._auth(self.login, self.password)
		if self.SID != None:
			return True
		return False

if __name__ == '__main__':
	foo = kartina('147', '741')
	foo.test()