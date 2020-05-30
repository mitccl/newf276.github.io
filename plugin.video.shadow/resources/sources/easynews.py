# -*- coding: utf-8 -*-
import requests,re
import time

global global_var,stop_all#global
global_var=[]
stop_all=0

 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,cloudflare_request,all_colors,base_header
from  resources.modules import cache

try:
    from resources.modules.general import Addon
except:
  import Addon
type=['movie','tv','non_rd']
SORT = {'s1': 'relevance', 's1d': '-', 's2': 'dsize', 's2d': '-', 's3': 'dtime', 's3d': '-'}
SEARCH_PARAMS = {'st': 'adv', 'sb': 1, 'fex': 'mkv, mp4, avi, mpg, wemb', 'fty[]': 'VIDEO', 'spamf': 1, 'u': '1', 'gx': 1, 'pno': 1, 'sS': 3}
SEARCH_PARAMS.update(SORT)
import urllib2,urllib,logging,base64,json
def _get_auth():

        auth = None
        
        username = Addon.getSetting('easynews.user')
        password = Addon.getSetting('easynews.password')
        
        if username == '' or password == '':
            return auth
        
        try:

            # Python 2
            user_info = '%s:%s' % (username, password)
            auth = 'Basic ' + base64.b64encode(user_info)
        
        except:

            # Python 3
            user_info = '%s:%s' % (username, password)
            user_info = user_info.encode('utf-8')
            auth = 'Basic ' + base64.b64encode(user_info).decode('utf-8')
        
        return auth
def normalize(title):
    import unicodedata
    try:
        try:
            return title.decode('ascii').encode("utf-8")
        except:
            pass

        return str(''.join(c for c in unicodedata.normalize('NFKD', unicode(title.decode('utf-8'))) if
                           unicodedata.category(c) != 'Mn'))
    except:
        return title
def _query( title,  season, episode,years,content_type):

        
        
        if content_type == 'movie':
            
            query = '"%s" %s' % (title, years)
        
        else:
            
            query = '%s S%02dE%02d' % (title,  int(season), int(episode))
        
        return query
def _translate_search( query,base_link,search_link):
		
		params = SEARCH_PARAMS
		params['pby'] = 100
		params['safeO'] = 1
		params['gps'] = params['sbj'] = query
		url = base_link + search_link
		
		return url, params
def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    from urllib import quote
    if Addon.getSetting("provider.easy")=='false':
        return []
    auth = _get_auth()

    if not auth:
        return
    
  
    
    
    all_links=[]
    base_link = 'https://members.easynews.com'
    search_link = '/2.0/search/solr-search/advanced'
    query = _query(clean_name(original_title,1),  season, episode,show_original_year,tv_movie)
    
    url, params = _translate_search(query,base_link,search_link)
    headers = {'Authorization': auth}
    response = requests.get(url, params=params, headers=headers).text
    results = json.loads(response)
    
    down_url = results.get('downURL')
    dl_farm = results.get('dlFarm')
    dl_port = results.get('dlPort')
    files = results.get('data', [])
    
    for item in files:
            post_hash, post_title, ext, duration = item['0'], item['10'], item['11'], item['14']
            
            checks = [False] * 5
            if 'alangs' in item and item['alangs'] and 'eng' not in item['alangs']: checks[1] = True
            if re.match('^\d+s', duration) or re.match('^[0-5]m', duration): checks[2] = True
            if 'passwd' in item and item['passwd']: checks[3] = True
            if 'virus' in item and item['virus']: checks[4] = True
            if 'type' in item and item['type'].upper() != 'VIDEO': checks[5] = True
            
            if any(checks):
                continue
            
            stream_url = down_url + quote('/%s/%s/%s%s/%s%s' % (dl_farm, dl_port, post_hash, ext, post_title, ext))
            title = post_title
            file_dl = stream_url + '|Authorization=%s' % (quote(auth))
            size = float(int(item['rawSize']))/1073741824
            
            
        
            if stop_all==1:
                break
            
            
            if '4k' in title:
                      res='2160'
            elif '2160' in title:
                  res='2160'
            elif '1080' in title:
                  res='1080'
            elif '720' in title:
                  res='720'
            elif '480' in title:
                  res='480'
            elif '360' in title:
                  res='360'
            else:
                  res='HD'
            
            
            max_size=int(Addon.getSetting("size_limit"))
              
            if size<max_size:
                all_links.append((title,file_dl,str(size),res))
           
                global_var=all_links
    return global_var
        
    