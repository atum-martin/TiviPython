import os
import sqlite3
import json
import http.server
import socketserver
import subprocess
import threading
import time

import PopulateDB
from urllib.parse import urlparse, parse_qs
from dateutil.parser import parse
import webbrowser

con = sqlite3.connect("tivi.db")
cur = con.cursor()


def openVideoPlayer(video_url):
    #await asyncio.create_subprocess_shell('"'+getVideoPlayerPath()+'" "'+video_url+'"', preexec_fn=os.setpgrp)
    p = subprocess.run([getVideoPlayerPath(), video_url])


def getVideoPlayerPath():
    players = [
        'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',
        'C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe',
        'C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe'
    ]
    for player in players:
        if os.path.isfile(player):
            return player

class TiviBackendHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def tiviBackend(self):
        print(self.path)
        query_components = parse_qs(urlparse(self.path).query)
        category = None
        if 'category' in query_components:
            category = query_components["category"][0]
        jsonReturn = []
        if 'get_services' in query_components["action"]:
            jsonReturn = getServices(category)
        if 'get_epg' in query_components["action"]:
            jsonReturn = getEpgAllGroup(category)
        if 'get_cats' in query_components["action"]:
            jsonReturn = getCategories()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(jsonReturn), "utf8"))

    def createM3U8(self):
        print(self.path)
        query_components = parse_qs(urlparse(self.path).query)

        video_url = query_components["video"][0]
        if video_url is None:
            self.send_response(404)

        self.send_response(200)
        self.send_header("Content-type", "application/vnd.apple.mpegurl")
        self.end_headers()
        m3u8 = '#EXTM3U\n#EXTINF:-1 tvg-id="streamid" tvg-name="streamname" tvg-logo="" group-title="group1"\n'+str(video_url)
        self.wfile.write(bytes(m3u8, "utf8"))


    def videoPlayerResponse(self):
        query_components = parse_qs(urlparse(self.path).query)
        video_url = query_components["video"][0]
        if video_url is None:
            self.send_response(404)
            return None
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps({}), "utf8"))
        return video_url


    def do_GET(self):
        if self.path == '/':
            self.path = 'app3.html'
        if '/backend.json' in self.path:
            return self.tiviBackend()
        elif self.path.startswith('/stream?'):
            video_url = self.videoPlayerResponse()
            if video_url is None:
                return
            methodCall = openVideoPlayer
            t = threading.Thread(target=methodCall, args=(video_url,))
            t.start()
            return
        else:
            self.path = 'html/'+self.path
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

def getCategories():
    cur = con.cursor()
    cates = []
    res = cur.execute("SELECT * FROM live_category")
    for row in res:
        cates.append({'id':row[0],'name':row[1]})
    return cates

def countRows():

    res = cur.execute("SELECT count(*) FROM epg")
    result = res.fetchone()
    print(str(result))

def getServices(category):
    if category is None:
        category = '1075'
    cur = con.cursor()
    services = []
    res = cur.execute("SELECT live_service.id, live_service.name, logo, live_category.name, url, live_category.id FROM live_service INNER JOIN live_category ON live_service.group_id = live_category.id WHERE live_category.id = '"+category+"' ORDER BY live_category.id ASC, live_service.id DESC")
    for row in res:
        thisService = {
            "channel_id": row[0],
            "channel_name": row[1],
            "logo": row[2],
            "group_name": row[3],
            "url": row[4],
            "group_id": row[5]
        }
        services.append(thisService)
    return services

def getServicesForEpg(category):
    if category is None:
        category = '1075'
    cur = con.cursor()
    services = []
    res = cur.execute("SELECT live_service.id FROM live_service INNER JOIN live_category ON live_service.group_id = live_category.id WHERE live_category.id = '"+category+"' ORDER BY live_category.id ASC, live_service.id ASC")
    for row in res:
        if row[0] != '' and row[0] not in services:
            services.append(row[0])
    return services

def getEpgAllGroup(category):
    cur = con.cursor()
    epg = []
    channelIds = getServicesForEpg(category)
    startTime = str(int(time.time() - (8*60*60)))
    endTime = str(int(time.time() + (32 * 60 * 60)))
    print('epg: '+startTime+' '+endTime)
    print('epg channel ids: '+str(channelIds))
    sql = "SELECT * FROM epg WHERE start >= "+startTime+" and start <= "+endTime+" and channelId IN ({seq}) ORDER BY channelId, start ASC".format(seq=','.join(['?'] * len(channelIds)))
    res = cur.execute(sql, channelIds)
    currentChannelId = ''
    currentChannelEpg = []
    i = 100
    for row in res:
        i += 1
        if currentChannelId != row[0] and len(currentChannelEpg) > 0:
            epg.append({"channel_id": currentChannelId, "epg": currentChannelEpg })
            currentChannelEpg = []
        currentChannelId = row[0]
        #channelId, start, stop, title, desc
        thisEpg = {
            "channelId": row[0],
            "start": row[1],
            "stop": row[2],
            "title": row[3],
            "desc": row[4]
        }
        currentChannelEpg.append(thisEpg)
    return epg

def parseTimestamp(timeStr):
    #20231019193000 +0200
    datetime = parse(timeStr, fuzzy=True)
    #print(str(datetime.timestamp()))
    return datetime.timestamp()

def getEpg(channelIds):
    cur = con.cursor()
    services = []
    sql = "SELECT * FROM epg WHERE channelId IN ({seq}) and start >= '20231028' and start <= '20231031' ORDER BY channelId, start DESC".format(seq=','.join(['?'] * len(channelIds)))
    res = cur.execute(sql, channelIds)
    i = 100
    for row in res:
        i += 1
        #channelId, start, stop, title, desc
        thisService = {
            "channelId": row[0],
            "start": parseTimestamp(row[1]),
            "stop": parseTimestamp(row[2]),
            "title": row[3],
            "desc": row[4]
        }
        services.append(thisService)
    return services

if __name__ == '__main__':
    print('PyCharm')
    PopulateDB.populateDatabase()
    countRows()
    print(str(json.dumps(getServices(None))))
    #print(str(getEpg(['de.Sky Cinema Hits'])))


    handler_object = TiviBackendHttpRequestHandler
    PORT = 8080
    http_server = socketserver.TCPServer(("", PORT), handler_object)
    webbrowser.open('http://127.0.0.1:8080/')
    http_server.serve_forever()

