import sqlite3
import json

con = sqlite3.connect("tivi.db")
cur = con.cursor()

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
    con.close()
    return services

def getEpg(channelIds):
    cur = con.cursor()
    services = []
    sql = "SELECT * FROM epg WHERE channelId IN ({seq}) and start >= '20231019' and start < '20231020' ORDER BY channelId, start DESC".format(seq=','.join(['?'] * len(channelIds)))
    res = cur.execute(sql, channelIds)
    i = 100
    for row in res:
        i += 1
        thisService = {
            "description": row[0],
            "duration": row[1],#int seconds
            "evtId": "",#int
            "hasTstv": "false",
            "image": "",
            "name": i,
            "startTime": "",#epoch in seconds
            "svcId": '1'}
        services.append(thisService)
    con.close()
    return services

if __name__ == '__main__':
    print('PyCharm')
    countRows()
    print(str(json.dumps(getServices())))
    #print(str(getEpg(['de.Sky Cinema Hits'])))

