
import requests
import json

class XtreamCodes:
    host = None
    username = None
    password = None
    baseUrl = None
    streamBaseUrl = None
    epgUrl = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 DMOST/2.0.0 (; LGE; webOSTV; WEBOS6.3.2 03.34.95; W6_lm21a;)'
    }

    def readServerConfig(self):
        f = open('settings.json')
        data = json.load(f)
        self.host = data['host']
        self.username = data['username']
        self.password = data['password']
        self.baseUrl = self.host+'/player_api.php?username='+self.username+'&password='+self.password+'&action='
        self.epgUrl = self.host + '/xmltv.php?username=' + self.username + '&password=' + self.password
        self.streamBaseUrl = self.host+'/'+self.username+'/'+self.password+'/'
        f.close()

    def getXtreamApi(self, path):
        print(self.baseUrl, path)
        x = requests.get(self.baseUrl+path, headers=self.headers)
        print(str(x.status_code))
        return x.json()

    def getVodCategories(self):
        return self.getXtreamApi('get_vod_categories')

    def getLiveCategories(self):
        liveCategories = self.getXtreamApi('get_live_categories')
        outputList = []
        priority = 0
        for category in liveCategories:
            priority = priority + 1
            outputList.append((category['category_id'], category['category_name'], priority))
        return outputList

    def getVodStreams(self):
        return self.getXtreamApi('get_vod_streams')

    def getLiveStreams(self):
        return self.getXtreamApi('get_live_streams')

    def getSeriesCategories(self):
        return self.getXtreamApi('get_series_categories')

    def getSeries(self):
        return self.getXtreamApi('get_series')

    def getSeriesInfo(self, seriesId):
        return self.getXtreamApi('get_series_info&series_id='+str(seriesId))

    def getVodInfo(self, vodId):
        return self.getXtreamApi('get_vod_info&vod_id='+str(vodId))

    def downloadEpg(self):
        self.downloadEpgSource(self.epgUrl)

    def downloadEpgSource(self, downloadUrl):
        x = requests.get(downloadUrl, headers=self.headers)
        print(str(x.status_code))
        with open("epg.xml", mode="wb") as file:
            file.write(x.content)
        print('epg downloaded and written')

    def getLiveServices(self):
        liveStreams = self.getLiveStreams()
        services = []
        for service in liveStreams:
            serviceUrl = self.streamBaseUrl+str(service['stream_id'])
            serviceEntry = (service['epg_channel_id'], service['name'], service['stream_icon'], service['category_id'], serviceUrl)
            services.append(serviceEntry)
        return services

if __name__ == '__main__':
    print('PyCharm')
    xstream = XtreamCodes()
    xstream.readServerConfig()
    print(str(xstream.getLiveCategories()))
    #print(str(xstream.getSeriesInfo(17470)))
