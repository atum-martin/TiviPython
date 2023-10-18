
import requests
import json

class XtreamCodes:
    host = None
    username = None
    password = None
    baseUrl = None

    def readServerConfig(self):
        f = open('settings.json')
        data = json.load(f)
        self.host = data['host']
        self.username = data['username']
        self.password = data['password']
        self.baseUrl = self.host+'/player_api.php?username='+self.username+'&password='+self.password+'&action='
        f.close()

    def getXtreamApi(self, path):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 DMOST/2.0.0 (; LGE; webOSTV; WEBOS6.3.2 03.34.95; W6_lm21a;)'
        }
        print(self.baseUrl, path)
        x = requests.get(self.baseUrl+path, headers=headers)
        print(str(x.status_code))
        return x.json()

    def getVodCategories(self):
        return self.getXtreamApi('get_vod_categories')

    def getLiveCategories(self):
        return self.getXtreamApi('get_live_categories')

    def getVodStreams(self):
        return self.getXtreamApi('get_vod_streams')

    def getLiveStreams(self):
        return self.getXtreamApi('get_live_streams')

if __name__ == '__main__':
    print('PyCharm')
    xstream = XtreamCodes()
    xstream.readServerConfig()
    print(str(xstream.getVodStreams()))