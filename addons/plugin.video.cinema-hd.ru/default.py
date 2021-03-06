#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import urllib
import simplejson as json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re,base64,random,time

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import unquote, quote, quote_plus
Addon = xbmcaddon.Addon( id = 'plugin.video.cinema-hd.ru' )
__language__ = Addon.getLocalizedString

addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

VERSION = '4.3as'
DOMAIN = '131896016'
GATrack='UA-30985824-2'
try:
    import platform
    xbmcver=xbmc.getInfoLabel( "System.BuildVersion" ).replace(' ','_').replace(':','_')
    UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s'% (xbmcver,platform.system(),platform.system(),platform.release(), platform.version(), platform.machine(),addon_id,addon_version,xbmcver)
except:
    UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))
hos = int(sys.argv[1])
headers  = {
    'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
    'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
    'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
    'Accept-Encoding':'identity, *;q=0'
}


def GET(target, post=None):
    #print target
    #print post
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        #req.add_header('Host',	'online.stepashka.com')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'ru-RU')
        resp = urllib2.urlopen(req)
        CE = resp.headers.get('content-encoding')
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
    
def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )
def doSearch(params):
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    out=''
    if kbd.isConfirmed():
        try:
            out = trans.detranslify(kbd.getText())
            out=str(out.encode("utf-8"))
        except:
            out = str(kbd.getText())
    #url='http://yandex.ru/sitesearch?text='+out+'&web=0&l10n=ru&frame=1&v=2.0&searchid=1891946&encoding=utf-8&topdoc=xdm_e%3Dhttp%253A%252F%252Fcinema-hd.ru%26xdm_c%3Ddefault4923%26xdm_p%3D1'
    #print url
    par={}
    par['url']='http://cinema-hd.ru/board'
    par['post']='query=%s&a=2'%out
    GetSearch(par)
    
    #data=GET('http://cinema-hd.ru/board','query=%s&a=2'%out)
   # print data
    
def GetSearch(params):
    http=GET(params['url'],params['post'])
    #href="(.+?)".+<span>(.+?)</span
    beautifulSoup = BeautifulSoup(http)
    m= re.findall('onclick="favor((.+?),(.+?),(.+?))"',str(beautifulSoup).replace("'",''))

    for n in m: 
        url= n[2].split('"')[0]
        img= n[3][0:len(n[3])-1]
        listitem=xbmcgui.ListItem(n[1][1:len(n[1])].replace('<b>','').replace('</b>','').replace('смотреть онлайн',''),iconImage = img, thumbnailImage = img)
        uri = construct_request({
            'func': 'get_movies',
            'url':url,
            'title':n[1].replace('<b>','').replace('</b>',''),
            'img':None
            })
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def run_settings(params):
    Addon.openSettings()

def mainMain(params):
    http = GET('http://cinema-hd.ru/')
    if http == None: return False
    listitem=xbmcgui.ListItem('Поиск',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'doSearch'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('ol',attrs={'class':'dsitemmenu'})
    content=content.findAll('li')
    listitem=xbmcgui.ListItem('Главная',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'mainScreen',
        'url':'board/0-1'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    listitem=xbmcgui.ListItem('Top 100',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'top100',
        'url':'index/top_100_films_cinema_hd_ru/0-25'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    for num in content:	
        title=num.find('a').string
        url=num.find('a')['href']
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url':url
            })

        if 'board' in url: xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def top100(params):
    host='http://cinema-hd.ru/index/top_100_films_cinema_hd_ru/0-25'
    http = GET(host)
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.findAll('table', attrs={'width': '700'})
    for n in content:
        
        txt=str(n)
        tt=re.findall('<div style="float:right"></div> <a href="(.+?)"><font face="Georgia" size="3;">(.+?)<font color="orange" face="Georgia" size="2;">',txt)
        url='http://cinema-hd.ru/'+tt[0][0]
        title=tt[0][1]
        try:
            desk=re.findall('<font size="1">(.+?)<hr /><font color="#ff9900">',txt)[0]
        except: desk="no"
        pic=re.findall('<img src="(.+?)" vspace="0" width="120" align="left" border="0" hspace="0" />',txt)[0]
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = pic)
        listitem.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
        uri = construct_request({
            'func': 'get_movies',
            'url':url,
            'title':title,
            'img':pic
            })
        print url
        xbmcplugin.addDirectoryItem(hos, uri, listitem,True)
        
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def mainScreen(params):
    host='http://cinema-hd.ru/'+params['url']
    try:
        page=(params['page'])
    except:
        page=1
    if page==1:
        http = GET(host)
    else: 
        if params['url']=='board/0-1':
            nhost=host.split('-')[0]+'-'+host.split('-')[1]+'-'+str(page)
            
        else: nhost=host+'-'+str(page)+'-2'

        http = GET(nhost)
    
    if http == None: return False
    
    beautifulSoup = BeautifulSoup(http)
    #print beautifulSoup
    #<table width="100%" cellspacing="1" cellpadding="1" border="0" style="padding-bottom: 1px;">
    content = beautifulSoup.findAll('div', attrs={'id': re.compile('entryID[0-9]+')})
    for n in content: 

        m= re.search('a href="(http://.+?)"',str(n))
        gg=re.findall('<font face="Georgia"><font color="3399cc">(.+?)</font><hr /><font size="2;" color="BEBEBE">(.+?)<hr />',str(n))
        try: desk= gg[0][1]
        except: desk='Нет описания'
        url= m.group(1)
        p = re.compile( 'title="(.+?)"' )
        #<span style="font-family:'Georgia'">Омамамия (2012)</span>

        m = re.findall('<span style="font-family:.+">(.+?)</span>',str(n))

        title= m[0]
        m= re.findall('<img src="(.+?)" vspace="0" width="250" ',str(n))
        pic= m[0]
        title=title.replace(' смотреть онлайн в хорошем качестве HD 720p бесплатно','')
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = pic)
        listitem.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
        uri = construct_request({
            'func': 'get_movies',
            'url':url,
            'title':title,
            'img':pic
            })
        #listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem,True)
    
    listitem=xbmcgui.ListItem('Next',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
                'func': 'mainScreen',
                'page':int(int(page)+1),
                'url':params['url']
                })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

from urllib import unquote, quote, quote_plus
    
    
def get_movies(params):
    http=GET(params['url'])
    #print params['url']
    beautifulSoup = BeautifulSoup(http)
    params['title']=params['title'].split("</font>")[0]
    txt=str(beautifulSoup).replace(' онлайн в хорошем качестве HD 720p','').replace(' онлайн в хорошем качестве','').replace('<font>Смотреть фильм ','').replace('<font>Смотреть сериал ','').replace('Смотреть онлайн фильм в хорошем качестве HD 720p','').replace('<font><font>','<font>').replace('<font></font>','').replace('<font> </font>','').replace('</font></font>','</font>')
    m=re.findall('<font>(?!.*Смотреть)(.+?)</font><br /><br /><iframe src="(.+?)"',txt)
    print txt
    if not m: m= re.findall('</font>(.+?)</font><br /><br /><iframe src="(.+?)"',txt)
    if not m: m= re.findall('</font>(.+?)</font></i><br /><br /><iframe src="(.+?)"',txt)

    for n in m: 

        listitem=xbmcgui.ListItem(n[0].split("</font>")[0].replace('смотреть онлайн',''),iconImage = addon_icon, thumbnailImage = params['img'])
        uri = construct_request({
            'func': 'get_movie',
            'url':n[1].replace('amp;','')
            })
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem)
    if not m: 

        m= re.findall('iframe src="(.+?)"',str(beautifulSoup))
        for n in m:
            listitem=xbmcgui.ListItem(params['title'].replace('смотреть онлайн',''),iconImage = addon_icon, thumbnailImage = params['img'])
            uri = construct_request({
                'func': 'get_movie',
                'url':n.replace('amp;','')
                })
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(hos, uri, listitem)
        
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def get_movie(params):

    http=GET(params['url'])
    #print http
    soup = BeautifulSoup(http, fromEncoding="windows-1251")
    av=0
    for rec in soup.findAll('param', {'name':'flashvars'}):
        #print rec
        for s in rec['value'].split('&'):
            if s.split('=',1)[0] == 'uid':
                uid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vtag':
                vtag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'host':
                host = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vid':
                vid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'oid':
                oid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd':
                hd = s.split('=',1)[1]
        host=host.replace('vk.me','vk.com')
        video = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
        qual=Addon.getSetting('qual')

        if int(hd)>=3 and int(qual)==3:
            #print 'aaa'
            video = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
        if int(hd)>=2 and int(qual)==2:
            video = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
        if int(hd)>=1 and int(qual)==1:
            video = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
        #print video
        item = xbmcgui.ListItem(path=video)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

            
    
def getinfo(param):
    info={}
    for infostring in param:
        try:
            m=re.search('[^<>]+<',str(infostring))
            comm = str( m.group(0)[:-1])
            m=re.search('[^<>]+</a',str(infostring))
            data = str( m.group(0)[:-3])
            #print "%s:%s"%(comm,data)
            if comm=="Год: ": info['year']=int(data)
            if comm=="Жанр: ": info['genre']=data
            if comm=="Режиссер: ": info['director']=data
            if comm=="Автор оригинала: ": info['writer']=data
        except: pass
    #print info
    return info

def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param

params = get_params(sys.argv[2])
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log( '[%s]: Primary input' % addon_id, 1 )
    mainMain(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)

