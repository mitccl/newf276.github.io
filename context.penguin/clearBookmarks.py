import xbmc


if __name__ == '__main__':
	plugin = 'plugin://plugin.video.penguin/'
	path = 'RunPlugin(%s?action=clearBookmarks&opensettings=false)' % plugin
	xbmc.executebuiltin(path)
