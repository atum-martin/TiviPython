import sqlite3
import xml.etree.ElementTree as ET
import M3UUtils
import XtreamCodesUtils

con = sqlite3.connect("tivi.db")
cur = con.cursor()

def createTables():
    try:
        cur.execute("DROP TABLE live_service")
        cur.execute("DROP TABLE epg")
        cur.execute("DROP TABLE live_category")
    except:
        print("tables don't exist")

    cur.execute("CREATE TABLE live_service(id, name, logo, groupName, url)")
    cur.execute("CREATE TABLE live_category(id, name, priority)")
    cur.execute("CREATE TABLE epg(channelId, start, stop, title, desc)")
    cur.fetchall()

def parseProgramme(prog):
    title = prog.find('title').text
    desc = prog.find('desc').text
    channel = prog.get('channel')
    start = prog.get('start')
    stop = prog.get('stop')
    print('programme '+channel+' '+start)
    return (channel, start, stop, title, desc)

def parseService(service):
    displayName = service.find('display-name').text
    id = service.get('id')
    print('service '+id+' '+displayName)
    return (id, displayName)

def parseEpgFile():
    tree = ET.parse('epg.xml')
    root = tree.getroot()
    services = []
    programmes = []
    for child in root:
        if 'programme' in child.tag:
            programmes.append(parseProgramme(child))
        if 'channel' in child.tag:
            services.append(parseService(child))

    print('progs: ' + str(len(programmes)))
    cur.executemany("INSERT INTO epg VALUES(?, ?, ?, ?, ?)", programmes)
    con.commit()

def parseXtreamServices():
    services = xstream.getLiveServices()
    servicesCategories = xstream.getLiveCategories()
    # services = M3UUtils.readM3U('input.m3u8')
    print('services: ' + str(len(services)))
    cur = con.cursor()
    cur.executemany("INSERT INTO live_service VALUES(?, ?, ?, ?, ?)", services)
    cur.executemany("INSERT INTO live_category VALUES(?, ?, ?)", servicesCategories)
    con.commit()

if __name__ == '__main__':
    print('PyCharm')
    createTables()
    xstream = XtreamCodesUtils.XtreamCodes()
    xstream.readServerConfig()
    xstream.downloadEpg()
    parseEpgFile()
    xstream.downloadEpgSource('https://raw.githubusercontent.com/atum-martin/astraepg/main/epg.xml')
    parseEpgFile()
    con.close()

