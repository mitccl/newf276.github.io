import xbmc


if __name__ == '__main__':
	plugin = 'plugin://plugin.video.penguin/'
	path = 'RunPlugin(%s?action=contextpenguinSettings&opensettings=false)' % plugin
	xbmc.executebuiltin(path)
	xbmc.executebuiltin('RunPlugin(%s?action=widgetRefresh)' % plugin)