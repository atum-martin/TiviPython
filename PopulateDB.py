import re
import sqlite3
import xml.etree.ElementTree as ET
import M3UUtils
import XtreamCodesUtils
import os
from dateutil.parser import parse
import pytz
import datetime

dbExists = os.path.isfile("tivi.db")

con = sqlite3.connect("tivi.db")
cur = con.cursor()

def truncateEpgTable():
    try:
        cur.execute("DELETE FROM epg")
        con.commit()
    except:
        print("tables epg don't exist")


def createTables():
    try:
        cur.execute("DROP TABLE live_service")
        cur.execute("DROP TABLE epg")
        cur.execute("DROP TABLE live_category")
    except:
        print("tables don't exist")

    cur.execute("CREATE TABLE live_service(id, name, logo, group_id, url)")
    cur.execute("CREATE TABLE live_category(id, name, priority)")
    cur.execute("CREATE TABLE epg(channelId, start, stop, title, desc)")
    con.commit()
    cur.fetchall()

def parseProgramme(prog):
    title = prog.find('title').text
    desc = prog.find('desc').text
    channel = prog.get('channel')
    start = parseTimestamp(prog.get('start'))
    stop = parseTimestamp(prog.get('stop'))
    #print('programme '+channel+' '+start)
    return (channel, start, stop, title, desc)

def parseService(service):
    displayName = service.find('display-name').text
    id = service.get('id')
    #print('service '+id+' '+displayName)
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

def getServicesCount():
    res = cur.execute("SELECT count(*) FROM live_service")
    result = res.fetchone()
    return int(result[0])


pp = re.compile(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2}) (\+|\-)(\d{2})(\d{2})')
def parseTimestamp(timeStr):
    #20231019193000 +0200

    match = pp.match(timeStr).groups()
    # datetime(year, month, day, hour, minute, second, microsecond)
    timeOffset = (int(match[7])*60*60)

    b = datetime.datetime(int(match[0]), int(match[1]), int(match[2]), int(match[3]), int(match[4]), int(match[5]), 0, pytz.timezone('UTC'))
    returnTime = b.timestamp()
    if match[6] == '+':
        returnTime = returnTime - timeOffset
    else:
        returnTime = returnTime + timeOffset

    #datetime2 = parse(timeStr, fuzzy=True)
    #print(str(datetime2.timestamp()))
    return returnTime

def parseXtreamServices(xstream):
    print('downloading services and cats')
    services = xstream.getLiveServices()
    servicesCategories = xstream.getLiveCategories()
    # services = M3UUtils.readM3U('input.m3u8')
    print('services: ' + str(len(services)))
    cur = con.cursor()
    cur.executemany("INSERT INTO live_service VALUES(?, ?, ?, ?, ?)", services)
    cur.executemany("INSERT INTO live_category VALUES(?, ?, ?)", servicesCategories)
    con.commit()

def populateDatabase():
    if dbExists is False:
        createTables()
    xstream = XtreamCodesUtils.XtreamCodes()
    xstream.readServerConfig()
    if dbExists is False or getServicesCount() == 0:
        parseXtreamServices(xstream)
    truncateEpgTable()
    xstream.downloadEpg()
    parseEpgFile()
    xstream.downloadEpgSource('https://raw.githubusercontent.com/atum-martin/astraepg/main/epg.xml')
    parseEpgFile()
    con.close()

#parseTimestamp('20231019193000 +0200')