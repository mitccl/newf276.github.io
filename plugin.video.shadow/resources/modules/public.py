import sys,urllib,logging,cache,json
import xbmcgui,xbmcplugin,xbmc,xbmcaddon,xbmcvfs,requests
global pre_mode

pre_mode=''
lang=xbmc.getLanguage(0)
Addon = xbmcaddon.Addon()
user_dataDir = xbmc.translatePath(Addon.getAddonInfo("profile")).decode("utf-8")
if not xbmcvfs.exists(user_dataDir+'/'):
     os.makedirs(user_dataDir)
def get_html_g():
    try:
        url_g='https://api.themoviedb.org/3/genre/tv/list?api_key=34142515d9d23817496eeb4ff1d223d0&language='+lang
        html_g_tv=requests.get(url_g).json()
         
   
        url_g='https://api.themoviedb.org/3/genre/movie/list?api_key=34142515d9d23817496eeb4ff1d223d0&language='+lang
        html_g_movie=requests.get(url_g).json()
    except Exception as e:
        logging.warning('Err in HTML_G:'+str(e))
    return html_g_tv,html_g_movie
html_g_tv,html_g_movie=cache.get(get_html_g,72, table='posters')
def addNolink( name, url,mode,isFolder,fanart='DefaultFolder.png', iconimage="DefaultFolder.png",plot=' ',year=' ',generes=' ',rating=' ',trailer=' ',original_title=' ',id=' ',season=' ',episode=' ' ,eng_name=' ',show_original_year=' ',dates=' ',dd=' ',dont_place=False):
 


            params={}
            params['name']=name
            params['iconimage']=iconimage
            params['fanart']=fanart
            params['description']=plot.replace("%27","'")
            params['url']=url
            params['original_title']=original_title
            params['id']=id
            params['season']=season
            params['episode']=episode
            params['eng_name']=episode
            params['show_original_year']=show_original_year
            params['dates']=dates
            params['dd']=dd
            menu_items=[]
            
            if mode==146 or mode==15:
                if mode==15:
                    tv_movie='movie'
                else:
                    tv_movie='tv'
                menu_items.append(('[I]Remove from series tracker[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&original_title=%s&mode=34&name=%s&id=0&season=%s&episode=%s')%(sys.argv[0],original_title,name,season,episode)))
                if len(id)>1:
                    if tv_movie=='tv':
                        tv_mov='tv'
                    else:
                        tv_mov='movie'
                    menu_items.append(('Queue item', 'Action(Queue)' ))
                    menu_items.append(('Trakt manager', 'XBMC.RunPlugin(%s)' % ('%s?url=%s&mode=150&name=%s&data=%s')%(sys.argv[0],id,original_title,tv_mov) ))
                    menu_items.append(('[I]Trakt watched[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&original_title=add&mode=65&name=%s&id=%s&season=%s&episode=%s')%(sys.argv[0],tv_movie,id,season,episode))) 
                    
                    menu_items.append(('[I]Trakt unwatched[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&original_title=remove&mode=65&name=%s&id=%s&season=%s&episode=%s')%(sys.argv[0],tv_movie,id,season,episode))) 
                    
                    type_info='extendedtvinfo'
                    if mode==15:
                        type_info='extendedinfo'
                    menu_items.append(('[I]OpenInfo[/I]','RunScript(script.extendedinfo,info=%s,dbid=,id=%s,name=%s,tvshow=%s,season=%s,episode=%s)'%(type_info,id,original_title,original_title,season,episode)))
        
            all_ur=utf8_urlencode(params)
            u=sys.argv[0]+"?&mode="+str(mode)+'&'+all_ur
            
            video_data={}
            video_data['title']=name
            
            
            if year!='':
                video_data['year']=year
            if generes!=' ':
                video_data['genre']=generes
            video_data['rating']=str(rating)
        
            #video_data['poster']=fanart
            video_data['plot']=plot.replace("%27","'")
            if trailer!='':
                video_data['trailer']=trailer
            
            liz = xbmcgui.ListItem( name, iconImage=iconimage, thumbnailImage=iconimage)

            liz.setInfo(type="Video", infoLabels=video_data)
            liz.setProperty( "Fanart_Image", fanart )
            liz.setProperty("IsPlayable","false")
            liz.addContextMenuItems(menu_items, replaceItems=False)
            art = {}
            art.update({'poster': iconimage})
            liz.setArt(art)
            if dont_place:
                return u,liz,False
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,isFolder=isFolder)
###############################################################################################################        
def utf8_urlencode(params):
    import urllib as u
    # problem: u.urlencode(params.items()) is not unicode-safe. Must encode all params strings as utf8 first.
    # UTF-8 encodes all the keys and values in params dictionary
    for k,v in params.items():
        # TRY urllib.unquote_plus(artist.encode('utf-8')).decode('utf-8')
        if type(v) in (int, long, float):
            params[k] = v
        else:
            try:
                params[k.encode('utf-8')] = v.encode('utf-8')
            except Exception as e:
                logging.warning( '**ERROR utf8_urlencode ERROR** %s' % e )
    
    return u.urlencode(params.items()).decode('utf-8')
def addDir3(name,url,mode,iconimage,fanart,description,premired=' ',image_master='',last_id='',video_info={},data=' ',original_title=' ',id=' ',season=' ',episode=' ',tmdbid=' ',eng_name=' ',show_original_year=' ',rating=0,heb_name=' ',isr=0,generes=' ',trailer=' ',dates=' ',watched='no',fav_status='false',collect_all=False,ep_number='',watched_ep='',remain='',hist='',join_menu=False,menu_leave=False,remove_from_fd_g=False,all_w={},mark_time=False,ct_date=''):
        name=name.replace("|",' ')
        description=description.replace("|",' ')
        original_title=original_title.replace("|",' ')
        
        params={}
        params['iconimage']=iconimage
        params['fanart']=fanart
        params['description']=description.replace("%27","'")
        params['url']=url
        params['name']=name
        params['image_master']=image_master
        params['heb_name']=heb_name
        params['last_id']=last_id
        params['dates']=dates
        params['data']=data
        params['original_title']=original_title
        params['id']=id
        params['season']=season
        params['episode']=episode
        params['tmdbid']=tmdbid
        params['eng_name']=eng_name
        params['show_original_year']=show_original_year
        params['isr']=isr
        params['fav_status']=fav_status
        params['all_w']=json.dumps(all_w)
        
        all_ur=utf8_urlencode(params)
        u=sys.argv[0]+"?mode="+str(mode)+'&'+all_ur
        ok=True
        show_sources=True
        try:
            a=int(season)
            check=True
        except:
            check=False
        if season!=None and season!="%20" and check:
              tv_movie='tv'
        else:
              tv_movie='movie'
        if mode==15:
            
            if tv_movie=='movie':
                se='one_click'
                
            else:
                se='one_click_tv'
            if Addon.getSetting(se)=='true':
                
                show_sources=False
            if Addon.getSetting("better_look")=='true':
                show_sources=False
        if (episode!=' ' and episode!='%20' and episode!=None) :
         
          tv_show='tv'
        else:
            tv_show='movie'
        menu_items=[]
        
        #menu_items.append(('[I]Info[/I]', 'Action(Info)'))
        if Addon.getSetting("play_trailer")=='true':
            menu_items.append(('[I]Play Trailer[/I]', 'XBMC.PlayMedia(%s)' % trailer))
        if Addon.getSetting("shadow_settings")=='true':
            menu_items.append(('Shadow settings', 'RunPlugin(%s?mode=151&url=www)' % sys.argv[0] ))
        if len(id)>1:
         
            if '/tv' in url or '/shows' in url:
                tv_mov='tv'
            else:
                tv_mov='movie'
            if Addon.getSetting("queue_item")=='true':
                menu_items.append(('Queue item', 'Action(Queue)' ))
            if Addon.getSetting("trakt_manager")=='true':
                menu_items.append(('Trakt manager', 'XBMC.RunPlugin(%s)' % ('%s?url=%s&mode=150&name=%s&data=%s')%(sys.argv[0],id,original_title,tv_mov) ))
            if Addon.getSetting("trakt_watched")=='true':
                menu_items.append(('[I]Trakt watched[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&original_title=add&mode=65&name=%s&id=%s&season=%s&episode=%s')%(sys.argv[0],tv_show,id,season,episode))) 
            if Addon.getSetting("trakt_unwatched")=='true':
                menu_items.append(('[I]Trakt unwatched[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&original_title=remove&mode=65&name=%s&id=%s&season=%s&episode=%s')%(sys.argv[0],tv_show,id,season,episode))) 
            if Addon.getSetting("openinfo")=='true':
                type_info='extendedinfo'
                if mode==16:
                    type_info='extendedtvinfo'
                if mode==19:
                    type_info='seasoninfo'
                if mode==15 and tv_movie=='tv':
                    type_info='extendedepisodeinfo'
                menu_items.append(('[I]OpenInfo[/I]','RunScript(script.extendedinfo,info=%s,dbid=,id=%s,name=%s,tvshow=%s,season=%s,episode=%s)'%(type_info,id,original_title,original_title,season,episode)))
        if mark_time:
            if Addon.getSetting("remove_resume_time")=='true':
                menu_items.append(('[I]Remove Resume time[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&mode=160&name=%s&id=%s&season=%s&episode=%s&data=%s')%(sys.argv[0],name,id,season,episode,tv_movie))) 
        if mode==15:
            u2=sys.argv[0]+"?mode="+str(16)+'&'+all_ur
            if Addon.getSetting("browse_series")=='true':
                menu_items.append(('Browse series', 'ActivateWindow(10025,"%s",return)' % (u2)))
        if mode==15 and hist=='true':
            if Addon.getSetting("remove_resume_point")=='true':
                menu_items.append(('[I]Remove resume point[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=%s&mode=159&name=%s&id=%s&season=%s&episode=%s')%(sys.argv[0],tv_show,name.replace("'",'%27').replace(",",'%28'),id,season,episode))) 
         
        if Addon.getSetting("clear_Cache")=='true':
            menu_items.append(('[I]Clear Cache[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=www&mode=35')%(sys.argv[0])))
        if Addon.getSetting("set_view_type")=='true' and Addon.getSetting("display_lock")=='true':
            menu_items.append(('[I]Set view type[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=%s&mode=167')%(sys.argv[0],str(pre_mode))))
        video_data={}
        video_data['title']=name
        if (episode!=' ' and episode!='%20' and episode!=None) :
          video_data['mediatype']='episode'
          video_data['TVshowtitle']=original_title
          video_data['Season']=int(str(season).replace('%20','0'))
          video_data['Episode']=int(str(episode).replace('%20','0'))
          
          if premired!=' ':
            video_data['premiered']=premired
          tv_show='tv'
        else:
           video_data['mediatype']='movie'
           video_data['TVshowtitle']=''
           #video_data['tvshow']=''
           video_data['season']=0
           video_data['episode']=0
           tv_show='movie'
        if  mode==7:
            tv_show='tv'
        video_data['OriginalTitle']=original_title
        if data!=' ':
            video_data['year']=data
        if generes!=' ':
            video_data['genre']=generes
        video_data['rating']=str(rating)
    
        #video_data['poster']=fanart
      
        video_data['plot']=description.replace("%27","'")
        video_data['Tag']=str(pre_mode)
        if ct_date!='':
            video_data['date']=ct_date
        if trailer!=' ':
            video_data['trailer']=trailer
        
        if watched=='yes':
          video_data['playcount']=1
          video_data['overlay']=7

        
        
        str_e1=list(u.encode('utf8'))
        for i in range(0,len(str_e1)):
           str_e1[i]=str(ord(str_e1[i]))
        str_e='$$'.join(str_e1)
        if tv_show=='tv':
            ee=str(episode)
        else:
            ee=str(id)
        if video_info!={}:
            
            video_data=video_info
        
        if ee in all_w:
            
            video_data['playcount']=0
            video_data['overlay']=0
            
           
            name=name.replace('[COLOR white]','[COLOR lightblue]')
            video_data['title']=name
            
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.addContextMenuItems(menu_items, replaceItems=False)
        if ep_number!='':
            
            liz.setProperty('totalepisodes', str(ep_number))
        if watched_ep!='':
             
               liz.setProperty('watchedepisodes', str(watched))

        if ee in all_w:
            #if mark_time:
            #   liz.setProperty('ResumeTime', all_w[ee]['resume'])
            #   liz.setProperty('TotalTime', all_w[ee]['totaltime'])
            try:
                if Addon.getSetting("filter_watched")=='true':
                    time_to_filter=float(Addon.getSetting("filter_watched_time"))
                    pre_time=float((float(all_w[ee]['resume'])*100)/float(all_w[ee]['totaltime']))
                    if pre_time>time_to_filter:
                        return u,None,show_sources
            except:
                pass
        
        art = {}
        art.update({'poster': iconimage})
        liz.setArt(art)
        video_data['title']=video_data['title'].replace("|",' ')
        video_data['plot']=video_data['plot'].replace("|",' ')
        video_streaminfo = {'codec': 'h264'}
                
        if len(id)>1:
            
            tt='Video'
        else:
            tt='Files'
   
        liz.setInfo( type=tt, infoLabels=video_data)
        liz.setProperty( "Fanart_Image", fanart )
        all_v_data=json.dumps(video_data)
        params={}
        params['video_data']=all_v_data
       
        all_ur=utf8_urlencode(params)
        u=u+'&'+all_ur
        
        art = {}
        art.update({'poster': iconimage})
        liz.setArt(art)
        #ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        if (Addon.getSetting("one_click")=='true' and mode==15):
            show_sources=False
        return u,liz,show_sources



def addLink( name, url,mode,isFolder, iconimage,fanart,description,place_control=False,data='',rating='',generes='',no_subs='0',tmdb='0',season='0',episode='0',original_title='',da='',year=0,all_w={},dd='',in_groups=False):
          name=name.replace("|",' ')
          description=description.replace("|",' ')
          episode=episode.replace('%20',' ')
          season=season.replace('%20',' ')

          params={}
          params['name']=name
          params['iconimage']=iconimage
          params['fanart']=fanart
          params['description']=description
          params['url']=url
          params['no_subs']=no_subs
          params['season']=season
          params['episode']=episode
          params['mode']=mode
          params['original_title']=original_title
          params['id']=tmdb
          params['dd']=dd
          params['data']=data
          params['nextup']='false'
          
          all_ur=utf8_urlencode(params)

          u=sys.argv[0]+"?"+'&'+all_ur
 

          video_data={}
          video_data['title']=name
            
            
          if year!='':
                video_data['year']=year
          if generes!='':
                video_data['genre']=generes
          if rating!=0:
            video_data['rating']=str(rating)
        
          #video_data['poster']=fanart
          video_data['plot']=description
          f_text_op=Addon.getSetting("filter_text")
          filer_text=False
          if len(f_text_op)>0:
                filer_text=True
                if ',' in f_text_op:
                    all_f_text=f_text_op.split(',')
                else:
                    all_f_text=[f_text_op]
            
          if filer_text:
            for items_f in all_f_text:
                if items_f.lower() in name.lower():
                    return 0
          
          liz = xbmcgui.ListItem( name, iconImage=iconimage, thumbnailImage=iconimage)
          menu_items=[]
          if Addon.getSetting("set_view_type")=='true':
            menu_items.append(('[I]Set view type[/I]', 'XBMC.RunPlugin(%s)' % ('%s?url=%s&mode=167')%(sys.argv[0],str(pre_mode))))
          if mode==170:
            menu_items.append(('[I]Remove from history[/I]', 'XBMC.RunPlugin(%s)' % ('%s?name=%s&url=www&id=%s&mode=171')%(sys.argv[0],name,tmdb)))
          liz.addContextMenuItems(menu_items, replaceItems=False)
          if in_groups:
              ee=str(name).replace("'","%27").encode('base64')
              
             
              if ee in all_w:
                
                video_data['playcount']=0
                video_data['overlay']=0
                video_data['title']='[COLOR lightblue]'+original_title+'[/COLOR]'
                liz.setProperty('ResumeTime', all_w[ee]['resume'])
                liz.setProperty('TotalTime', all_w[ee]['totaltime'])
                try:
                    if Addon.getSetting("filter_watched")=='true':
                        time_to_filter=float(Addon.getSetting("filter_watched_time"))
                        pre_time=float((float(all_w[ee]['resume'])*100)/float(all_w[ee]['totaltime']))
                        if pre_time>time_to_filter:
                            return 0
                except:
                    pass
          liz.setInfo(type="Video", infoLabels=video_data)
          art = {}
          art.update({'poster': iconimage})
          liz.setArt(art)
          liz.setProperty("IsPlayable","true")
          liz.setProperty( "Fanart_Image", fanart )
          if place_control:
            return u,liz,False
          xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,isFolder=isFolder)