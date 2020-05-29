import sys, xbmc, json

try:
	from urlparse import parse_qsl
except:
	from urllib.parse import parse_qsl


if __name__ == '__main__':
	item = sys.listitem
	path = item.getPath()
	plugin = 'plugin://plugin.video.penguin/'
	args = path.split(plugin, 1)
	params = dict(parse_qsl(args[1].replace('?', '')))

	year = params.get('year')
	name = params.get('title') + ' (%s)' % year
	if 'tvshowtitle' in params:
		season = params.get('season', '')
		episode = params.get('episode', '')
		name = params.get('tvshowtitle') + ' S%02dE%02d' % (int(season), int(episode))

	path = 'RunPlugin(%s?action=clearBookmark&name=%s&year=%s&opensettings=false)' % (plugin, name, year)
	xbmc.executebuiltin(path)
	item.setProperty('resumetime', '0') # Kodi seems to still show cm resume options but resume indicator is gone
	xbmc.executebuiltin('RunPlugin(%s?action=widgetRefresh)' % plugin)
