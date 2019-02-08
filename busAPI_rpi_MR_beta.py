from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from requests import request
from pprint import pprint
import  json
import demjson
import os
import time
from datetime import datetime
import socket

app_id = 'c2867a08b8f741b9bef1900b2c12c55a'
app_key = 'ebQiA77NHGeX_pi-HnWxlmuTU1g'

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }

def internet(host="8.8.8.8", port=53, timeout=3):
      """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
      except Exception as ex:
        print (ex.message)
        return False

def programset():
    global var
    global routejson
    global routelist
    global bus_list
    global bustmp_list
    global buscount
    global maxcount
    global totalcount
    global writechk
    try :
        fp1 = open("./start.txt","r")
        chk = fp1.read()
        fp1.close()
        if int(chk) == 1 :
            var = 1
        else :
            var = 0
        fp2 = open("./routeset.txt","r")
        routejson = demjson.decode(fp2.read())
        fp2.close()
    except :
        var = 0
    routelist = []
    for item in routejson:
        if item["RouteID"] not in routelist :
            routelist.append(item["RouteID"])
    bus_list = {}
    bustmp_list = {}
    buscount = {}
    maxcount = {}
    totalcount = {}
    writechk ={}
    for i in routelist:
        bus_list['bus_'+str(i)] = []
        maxcount['bus_'+str(i)] = 0
        totalcount['bus_'+str(i)] = 0
        writechk['bus_'+str(i)] = 0

if __name__ == '__main__' :
    while internet() == False :
        time.sleep(2)
    programset()
    timechk = 1
    var1 = 0
    var2 = 0
    while var == 1 :
        wrerr = 0
        stachk = 0
        try :
            if datetime.now().strftime("%H") == "23" and var1 == 0 :
                timechk = 0
                print("System Sleep")
                ft1 = open( "./businfo_MR.html", "w")
                ft1.write("Non-working hours")
                ft1.close()
                var1 = 1
                var2 = 0
            if datetime.now().strftime("%H%M") == "0600" :
                programset()
                timechk = 1
                var1 = 0
        except :
            wrerr = 1

        for i in routelist:
            bustmp_list['bus_'+str(i)] = []
            buscount['bus_'+str(i)] = 0

        if wrerr == 0 and timechk == 1:
            for item in routejson:
                Sourcetype = item["Sourcetype"]
                Region = item["Region"]
                RouteID = item["RouteID"]
                err = 0
                try :
                    a = Auth(app_id, app_key)
                    response = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/' + Sourcetype + '/' + Region + '/' + RouteID + '?$top=50&$select=PlateNumb&$format=JSON', headers= a.get_auth_header())        
                    decodejson =  demjson.decode(response.content)
                except :
                    err = 1
                    stachk = 1
                    var2 += 1

                if err == 0 :
                    try :
                        for item in decodejson :
                            if item.get('DutyStatus' , 2) != 2 :
                                if item['PlateNumb'] not in bustmp_list['bus_'+str(RouteID)] :
                                    buscount['bus_'+str(RouteID)] += 1
                                    bustmp_list['bus_'+str(RouteID)].append(item['PlateNumb'])
                                if item['PlateNumb'] not in bus_list['bus_'+str(RouteID)] :
                                    totalcount['bus_'+str(RouteID)] += 1
                                    bus_list['bus_'+str(RouteID)].append(item['PlateNumb'])
                                    tmp = bus_list['bus_'+str(RouteID)][len(bus_list['bus_'+str(RouteID)])-1]
                                    j = len(bus_list['bus_'+str(RouteID)]) - 2
                                    while j >= 0 and tmp < bus_list['bus_'+str(RouteID)][j] :
                                        bus_list['bus_'+str(RouteID)][j + 1] = bus_list['bus_'+str(RouteID)][j]
                                        j = j - 1
                                    bus_list['bus_'+str(RouteID)][ j + 1 ] = tmp
                                    writechk['bus_'+str(RouteID)] = 1
                        if buscount['bus_'+str(RouteID)] > maxcount['bus_'+str(RouteID)] :
                            maxcount['bus_'+str(RouteID)] = buscount['bus_'+str(RouteID)]
                    except :
                        stachk = 2

            try :
                path = "./businfo_MRB/"  + datetime.now().strftime("%Y%m%d")
                if not os.path.isdir(path) :
                    os.mkdir(path)
                fp3 = open( path +  "/" + datetime.now().strftime("%Y%m%d") + "_" + "hour=" + datetime.now().strftime("%H") + ".txt", "a")
                ft2 = open( "./businfo_MR.html", "w")
                op = 0
            except :
                op = 1

            if op == 0 :
                try:
                    ft2.write( '<head><meta http-equiv="refresh" content="5" /><head>' )
                    for i in range(len(routelist)) :
                        if writechk['bus_'+str(routelist[i])] == 1 :
                            print("System work")
                            var2 = 0
                            value = 0
                            fp3.write( str(routelist[i]) + " 今日車輛:(目前:" + str(buscount['bus_'+str(routelist[i])]) + "輛,最高:" + str(maxcount['bus_'+str(routelist[i])]) + "輛,總數:" + str(totalcount['bus_'+str(routelist[i])]) + "輛)" + "\n")
                            ft2.write( str(routelist[i]) + " 今日車輛:(目前:" + str(buscount['bus_'+str(routelist[i])]) + "輛,最高:" + str(maxcount['bus_'+str(routelist[i])]) + "輛,總數:" + str(totalcount['bus_'+str(routelist[i])]) + "輛)" + "<br>")
                            for item in bus_list['bus_'+str(routelist[i])] :
                                tag = 0
                                if value != 0 :
                                    fp3.write( "," )
                                    ft2.write( "," )
                                if buscount['bus_'+str(routelist[i])] != 0 :
                                    for items in bustmp_list['bus_'+str(routelist[i])] :
                                        if items == item :
                                            fp3.write("[")
                                            ft2.write("[")
                                            tag = 1
                                fp3.write(str(item))
                                ft2.write(str(item))
                                if tag == 1 :
                                    fp3.write("]")
                                    ft2.write("]")
                                value += 1
                            fp3.write( "\n\n" )
                            ft2.write( "<p>" )
                except :
                    print("Write Error")
                    
            try :
                fp3.write("資料最後更新時間 : %s \n\n\n" % time.ctime())
                ft2.write("資料最後更新時間 : %s <br>" % time.ctime())
                fp3.close()
                ft2.close()
                if stachk == 1 :
                    ft3 = open( "./businfo_MR.html", "a")
                    ft3.write("PTX Platform Error! <br>")
                    ft3.close()
                if stachk == 2 :
                    ft4 = open( "./businfo_MR.html", "a")
                    ft4.write("Decodejson Error! <br>")
                    ft4.close()
            except :
                print("Write Time Error")

        if var2 < 20 :
            try :
                time.sleep( 60 - int(datetime.now().strftime("%S")))
            except :
                time.sleep( 60 )
        else :
            try :
                ft5 = open( "./businfo_MR.html", "a")
                ft5.write("System out of service because of PTX platform error <br>")
                ft5.close()
            except :
                print("Write Error01")
            time.sleep( 1200 )
        
            