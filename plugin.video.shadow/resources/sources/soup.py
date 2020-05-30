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

import urllib2,urllib,logging,base64,json


def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all

   
    
  
    
    
    all_links=[]
    headers = {
        'authority': 'soap2day.is',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://soap2day.is',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
 
        'accept-language': 'en-US,en;q=0.9',
        
    }

    from resources.modules.general import cloudflare_request

    uri='https://soap2day.is/search/keyword/%s/'%clean_name(original_title,1).replace(' ','%20')
    
    a,cook=cloudflare_request(uri,headers=headers)

    res='<div class="img-group">(.+?)></h5>'
    m_pre=re.compile(res,re.DOTALL).findall(a)
    
    for items in m_pre:
        regex='style="padding\:3">(.+?)<.+?<h5><a href=(?:"|\')(.+?)(?:"|\')>(.+?)<'
        m=re.compile(regex,re.DOTALL).findall(items)
        
        for yr,lk,nm in m:
            yr=yr.replace('-','')
            
            if show_original_year in yr and clean_name(original_title,1).lower()==nm.replace(':','%3a').lower():
                
                x=requests.get('https://soap2day.is'+lk,headers=cook[1],cookies=cook[0]).content
                y=x
                
                if tv_movie=='tv':
                    regex='<h4>Season%s .+?a href="(.+?)">%s.'%(season,episode)
                    mm=re.compile(regex).findall(x)[0]
                    mm=mm.split('<div class="col-sm-12 col-md-6 col-lg-4 myp1"><a href="')
                    llk=mm[len(mm)-1]
                   
                    y=requests.get('https://soap2day.is'+llk,headers=cook[1],cookies=cook[0]).content
               
                regex='type="hidden" id="hId" value="(.+?)"'
                did=re.compile(regex).findall(y)[0]
                
                cook[1]['Referer']= 'https://soap2day.is'+lk
                data = {
                  'pass': did
                }
           
                if tv_movie=='tv':
                    added='GetEInfoAjax'
                else:
                    added='GetMInfoAjax'
              
                response=requests.post('https://soap2day.is/home/index/'+added, headers=cook[1],cookies=cook[0], data=data).content
                
                #response,cook2 = cloudflare_request('https://soap2day.is/home/index/'+added, headers=headers, post=data)
               
                j_res=json.loads(response)
                f_link=j_res['val']
                if tv_movie=='tv':
                    title=clean_name(original_title,1)+'.S%sE%s'%(season_n,episode_n)
                else:
                    title=clean_name(original_title,1)
                if 'subs' in j_res:
                 if (j_res['subs'])!=None:
                    title=j_res['subs'][0]['source_file_name'].replace('.srt','')
                try_head = requests.head(f_link,headers=base_header, stream=True,verify=False,timeout=15)
                f_size2=0
                if 'Content-Length' in try_head.headers:
          
                    if int(try_head.headers['Content-Length'])>(1024*1024):
                        f_size2=str(round(float(try_head.headers['Content-Length'])/(1024*1024*1024), 2))
                all_links.append((title,'Direct_link$$$'+f_link,str(f_size2),'720'))
                       
                global_var=all_links
                
    return global_var
        
    