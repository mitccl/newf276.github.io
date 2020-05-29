# -*- coding: utf-8 -*-

'''
	penguin Add-on
'''

import json
import re
import requests

from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import workers
try:
	from resolveurl.plugins.realdebrid import RealDebridResolver
except:
	pass


CLIENT_ID = 'X245A4XAIBGVM'
USER_AGENT = 'ResolveURL for Kodi/%s' % control.getKodiVersion()


rest_base_url = 'https://api.real-debrid.com/rest/1.0/'
oauth_base_url = 'https://api.real-debrid.com/oauth/v2'
unrestrict_link_path = 'unrestrict/link'
device_endpoint_path = 'device/code'
token_endpoint_path = 'token'
authorize_endpoint_path = 'auth'
credentials_endpoint_path = 'device/credentials'
hosts_regexes_path = 'hosts/regex'
hosts_domains_path = 'hosts/domains'
add_magnet_path = 'torrents/addMagnet'
torrents_info_path = 'torrents/info'
select_files_path = 'torrents/selectFiles'
torrents_delete_path = 'torrents/delete'
check_cache_path = 'torrents/instantAvailability'


class RealDebrid:
	def __init__(self):
		self.token = RealDebridResolver.get_setting('token')
		self.hosters = None
		self.hosts = None
		self.headers = {'User-Agent': USER_AGENT, 'Authorization': 'Bearer %s' % self.token}
		self.cache_check_results = {}


	def get_url(self, url, fail_check=False, token_ck=False):
		original_url = url
		url = rest_base_url + url
		if self.token == '':
			log_utils.log('No Real Debrid Token Found', __name__, log_utils.LOGDEBUG)
			return None
		# if not fail_check: # with fail_check=True new token does not get added
		if '?' not in url:
			url += "?auth_token=%s" % self.token
		else:
			url += "&auth_token=%s" % self.token

		response = requests.get(url, timeout=5).text

		if 'bad_token' in response or 'Bad Request' in response:
			if not fail_check:
				if self.refresh_token() and token_ck:
					return
				response = self.get_url(original_url, fail_check=True)
		try:
			return json.loads(response)
		except:
			return response


	def check_cache_list(self, hashList):
		if isinstance(hashList, list):
			hashList = [hashList[x:x+100] for x in range(0, len(hashList), 100)]
			# Need to check token, and refresh if needed, before blasting threads at it
			ck_token = self.get_url('user', token_ck=True)

			threads = []
			for section in hashList:
				threads.append(workers.Thread(self.check_hash_thread, section))
			[i.start() for i in threads]
			[i.join() for i in threads]

			return self.cache_check_results
		else:
			hashString = "/" + hashList
			return self.get_url("torrents/instantAvailability" + hashString)


	def check_hash_thread(self, hashes):
		try:
			hashString = '/' + '/'.join(hashes)
			response = self.get_url("torrents/instantAvailability" + hashString)
			# log_utils.log('response = %s' % response, __name__, log_utils.LOGDEBUG)
			self.cache_check_results.update(response)
		except:
			log_utils.error()
			pass


	def __torrent_info(self, torrent_id):
		try:
			url = '%s/%s/%s' % (rest_base_url, torrents_info_path, torrent_id)
			result = self.net.http_GET(url, headers=self.headers).content
			js_result = json.loads(result)
			return js_result
		except Exception as e:
			log_utils.log('Real-Debrid Error: TORRENT INFO | %s' % e, __name__, log_utils.LOGDEBUG)
			raise


	def __add_magnet(self, media_id):
		try:
			url = '%s/%s' % (rest_base_url, add_magnet_path)
			data = {'magnet': media_id}
			result = self.net.http_POST(url, form_data=data, headers=self.headers).content
			js_result = json.loads(result)
			log_utils.log('Real-Debrid: Sending MAGNET URL to the real-debrid cloud', __name__, log_utils.LOGDEBUG)
			return js_result.get('id', "")
		except Exception as e:
			log_utils.log('Real-Debrid Error: ADD MAGNET | %s' % e, __name__, log_utils.LOGDEBUG)
			raise


	def __select_file(self, torrent_id, file_id):
		try:
			url = '%s/%s/%s' % (rest_base_url, select_files_path, torrent_id)
			data = {'files': file_id}
			self.net.http_POST(url, form_data=data, headers=self.headers)
			log_utils.log('Real-Debrid: Selected file ID %s from Torrent ID %s to transfer' % (file_id, torrent_id), __name__, log_utils.LOGDEBUG)
			return True
		except Exception as e:
			log_utils.log('Real-Debrid Error: SELECT FILE | %s' % e, __name__, log_utils.LOGDEBUG)
			return False


	def __delete_torrent(self, torrent_id):
		try:
			url = '%s/%s/%s' % (rest_base_url, torrents_delete_path, torrent_id)
			self.net.http_DELETE(url, headers=self.headers)

			log_utils.log('Real-Debrid: Torrent ID %s was removed from your active torrents' % torrent_id, __name__, log_utils.LOGDEBUG)
			return True
		except Exception as e:
			log_utils.log('Real-Debrid Error: DELETE TORRENT | %s' % e, __name__, log_utils.LOGDEBUG)
			raise


	def __get_link(self, link):
		if 'download' in link:
			if 'quality' in link:
				label = '[%s] %s' % (link['quality'], link['download'])
			else:
				label = link['download']
			return label, link['download']


	# SiteAuth methods
	def login(self):
		if not self.get_setting('token'):
			self.authorize_resolver()


	def refresh_token(self):
		try:
			client_id = RealDebridResolver.get_setting('client_id')
			client_secret = RealDebridResolver.get_setting('client_secret')
			refresh_token = RealDebridResolver.get_setting('refresh')

			log_utils.log('Refreshing Expired Real Debrid Token: |%s|%s|' % (client_id, refresh_token), __name__, log_utils.LOGDEBUG)

			if not self.__get_token(client_id, client_secret, refresh_token):
				# empty all auth settings to force a re-auth on next use
				self.reset_authorization()
				log_utils.log('Unable to Refresh Real Debrid Token', __name__, log_utils.LOGDEBUG)
			else:
				log_utils.log('Real Debrid Token Successfully Refreshed', __name__, log_utils.LOGDEBUG)
				return True
		except:
			return False

	def authorize_resolver(self):
		url = '%s/%s?client_id=%s&new_credentials=yes' % (oauth_base_url, device_endpoint_path, CLIENT_ID)
		js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
		line1 = 'Go to URL: %s' % (js_result['verification_url'])
		line2 = 'When prompted enter: %s' % (js_result['user_code'])
		with common.kodi.CountdownDialog('Resolve URL Real Debrid Authorization', line1, line2, countdown=120, interval=js_result['interval']) as cd:
			result = cd.start(self.__check_auth, [js_result['device_code']])

		# cancelled
		if result is None:
			return
		return self.__get_token(result['client_id'], result['client_secret'], js_result['device_code'])


	def __get_token(self, client_id, client_secret, code):
		try:
			url = '%s/%s' % (oauth_base_url, token_endpoint_path)
			postData = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}

			RealDebridResolver.set_setting('client_id', client_id)
			RealDebridResolver.set_setting('client_secret', client_secret)

			log_utils.log('Authorizing Real Debrid: %s' % client_id, __name__, log_utils.LOGDEBUG)

			response = requests.post(url, data=postData).text
			response = json.loads(response)

			log_utils.log('Authorizing Real Debrid Result: |%s|' % response, __name__, log_utils.LOGDEBUG)
			self.token = response['access_token']
			RealDebridResolver.set_setting('token', self.token)
			RealDebridResolver.set_setting('refresh', response['refresh_token'])

			return True
		except Exception as e:
			log_utils.log('Real Debrid Authorization Failed: %s' % e, __name__, log_utils.LOGDEBUG)
			return False


	def __check_auth(self, device_code):
		try:
			url = '%s/%s?client_id=%s&code=%s' % (oauth_base_url, credentials_endpoint_path, CLIENT_ID, device_code)
			js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
		except Exception as e:
			log_utils.log('Exception during RD auth: %s' % e, __name__, log_utils.LOGDEBUG)
		else:
			return js_result


	def reset_authorization(self):
		RealDebridResolver.set_setting('client_id', '')
		RealDebridResolver.set_setting('client_secret', '')
		RealDebridResolver.set_setting('token', '')
		RealDebridResolver.set_setting('refresh', '')


	def get_host_and_id(self, url):
		return 'www.real-debrid.com', url


	def get_all_hosters(self):
		hosters = []
		try:
			url = '%s/%s' % (rest_base_url, hosts_regexes_path)
			js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
			regexes = [regex[1:-1].replace('\/', '/').rstrip('\\') for regex in js_result]
			log_utils.log('RealDebrid hosters : %s' % regexes, __name__, log_utils.LOGDEBUG)
			hosters = [re.compile(regex, re.I) for regex in regexes]
		except Exception as e:
			log_utils.log('Error getting RD regexes: %s' % e, __name__, log_utils.LOGDEBUG)
		return hosters


	def get_hosts(self):
		hosts = []
		try:
			url = '%s/%s' % (rest_base_url, hosts_domains_path)
			hosts = json.loads(self.net.http_GET(url, headers=self.headers).content)
			if self.get_setting('torrents') == 'true':
				hosts.extend([u'torrent', u'magnet'])
		except Exception as e:
			log_utils.log('Error getting RD hosts: %s' % e, __name__, log_utils.LOGDEBUG)
		log_utils.log('RealDebrid hosts : %s' % hosts, __name__, log_utils.LOGDEBUG)
		return hosts


	@classmethod
	def _is_enabled(cls):
		return cls.get_setting('enabled') == 'true' and cls.get_setting('token')


	def valid_url(self, url, host):
		log_utils.log('in valid_url %s : %s' % (url, host), __name__, log_utils.LOGDEBUG)
		if url:
			if url.lower().startswith('magnet:') and self.get_setting('torrents') == 'true':
				return True
			if self.hosters is None:
				self.hosters = self.get_all_hosters()

			for host in self.hosters:
				log_utils.log('RealDebrid checking host : %s' % str(host), __name__, log_utils.LOGDEBUG)
				if re.search(host, url):
					log_utils.log('RealDebrid Match found', __name__, log_utils.LOGDEBUG)
					return True
		elif host:
			if self.hosts is None:
				self.hosts = self.get_hosts()

			if host.startswith('www.'):
				host = host.replace('www.', '')
			if any(host in item for item in self.hosts):
				return True
		return False


	@classmethod
	def get_settings_xml(cls):
		xml = super(cls, cls).get_settings_xml()
		xml.append('<setting id="%s_torrents" type="bool" label="%s" default="true"/>' % (cls.__name__, i18n('torrents')))
		xml.append('<setting id="%s_cached_only" enable="eq(-1,true)" type="bool" label="%s" default="false" />' % (cls.__name__, i18n('cached_only')))
		xml.append('<setting id="%s_autopick" type="bool" label="%s" default="false"/>' % (cls.__name__, i18n('auto_primary_link')))
		xml.append('<setting id="%s_auth" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)"/>' % (cls.__name__, i18n('auth_my_account')))
		xml.append('<setting id="%s_reset" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_rd)"/>' % (cls.__name__, i18n('reset_my_auth')))
		xml.append('<setting id="%s_token" visible="false" type="text" default=""/>' % cls.__name__)
		xml.append('<setting id="%s_refresh" visible="false" type="text" default=""/>' % cls.__name__)
		xml.append('<setting id="%s_client_id" visible="false" type="text" default=""/>' % cls.__name__)
		xml.append('<setting id="%s_client_secret" visible="false" type="text" default=""/>' % cls.__name__)
		return xml

	@classmethod
	def isUniversal(cls):
		return True