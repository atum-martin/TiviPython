import sqlite3
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

con = sqlite3.connect("tivi.db")
cur = con.cursor()

class TiviBackendHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def tiviBackend(self):
        print(self.path)
        query_components = parse_qs(urlparse(self.path).query)

        jsonReturn = []
        if 'get_services' in query_components["action"]:
            jsonReturn = getServices()
        if 'get_epg' in query_components["action"]:
            jsonReturn = getEpg((query_components["channel_id"]))

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
        self.send_header("Content-type", "application/x-mpegURL")
        self.end_headers()
        m3u8 = '#EXTM3U\n#EXTINF:-1 tvg-id="streamid" tvg-name="streamname" tvg-logo="" group-title="group1"\n'+str(video_url)
        self.wfile.write(bytes(m3u8, "utf8"))

    def do_GET(self):
        if self.path == '/':
            self.path = 'app3.html'
        if '/backend.json' in self.path:
            return self.tiviBackend()
        elif '/stream?' in self.path:
            return self.createM3U8()
        else:
            self.path = 'html/'+self.path
            return http.server.SimpleHTTPRequestHandler.do_GET(self)



def countRows():

    res = cur.execute("SELECT count(*) FROM epg")
    result = res.fetchone()
    print(str(result))

def getServices():
    cur = con.cursor()
    services = []
    res = cur.execute("SELECT live_service.id, live_service.name, logo, live_category.name, url, live_category.id FROM live_service INNER JOIN live_category ON live_service.group_id = live_category.id WHERE live_category.id = '1075' ORDER BY live_category.id ASC, live_service.id ASC")
    i = 100
    for row in res:

        if row[0] == '':
            continue

        if i >= 120:
            return services
        i += 1
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

def getEpg(channelIds):
    cur = con.cursor()
    services = []
    sql = "SELECT * FROM epg WHERE channelId IN ({seq}) and start >= '20231019' and start < '20231020' ORDER BY channelId, start DESC".format(seq=','.join(['?'] * len(channelIds)))
    res = cur.execute(sql, channelIds)
    i = 100
    for row in res:
        i += 1
        #channelId, start, stop, title, desc
        thisService = {
            "channelId": row[0],
            "start": row[1],
            "stop": row[2],
            "title": row[3],
            "desc": row[4]
        }
        services.append(thisService)
    return services

if __name__ == '__main__':
    print('PyCharm')
    countRows()
    print(str(json.dumps(getServices())))
    #print(str(getEpg(['de.Sky Cinema Hits'])))

    handler_object = TiviBackendHttpRequestHandler
    PORT = 8080
    http_server = socketserver.TCPServer(("", PORT), handler_object)
    http_server.serve_forever()

