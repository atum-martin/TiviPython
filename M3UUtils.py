import codecs
import requests
import re

def parseM3U(content):
    regex = '#EXTINF:-1 tvg-id="(.*)" tvg-name="(.*)" tvg-logo="(.*)" group-title="(.*)",(.*)'
    #tvgId, name, logo, group, displayName, url = None
    services = []
    for line in content:
        matches = re.match(regex, line)
        if matches is not None:
            tvgId = matches.group(1).strip()
            tvgName = matches.group(2).strip()
            logo = matches.group(3).strip()
            group = matches.group(4).strip()
            displayName = matches.group(5).strip()
        elif '#EXT' in line:
            pass
        else:
            url = line
            services.append((tvgId, displayName, logo, group, url))
    return services

def readM3U(path):
    file = codecs.open(path, encoding='utf-8')
    services = parseM3U(file.readlines())
    file.close()
    return services

def downloadM3U(url):
    x = requests.get('https://somebody.com/get.php?username=hello&password=test')
    print(str(x.status_code))
    services = parseM3U(x.text)
    return services

if __name__ == '__main__':
    print('PyCharm')