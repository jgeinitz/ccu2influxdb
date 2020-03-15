#!/usr/bin/python3
import json
import pycurl

debugging=0

class send_to_influxdb:
    global debugtext
    global debugtime
    connection=""
    def __init__(self):
        self.connection = pycurl.Curl()
        self.connection.setopt(self.connection.URL,
                               "http://127.1:9999/write?db=weather")

    def insert_record(self,string):
        self.connection.setopt(self.connection.POSTFIELDS, str(string))
        self.connection.perform()

class w:

    tags=''
    values=''

    def __init__(self):
        with open("/disk/tmp/wetterreport", 'r') as wetter:
            data = wetter.read()

        obj = json.loads(data)

        #print(data)

        values=" "
        tags = "coordlon_tag="+ str(obj['coord']['lon'])+","+"coordlat_tag="+str(obj['coord']['lat'])
        tags += ",name_tag="+ str(obj['name'])
        #for l in obj['weather']:
        #    values += "weather_" + str(l['id']) + '_main="' + str(l['main']) +'",'
        #    values += "weather_" + str(l['id']) + '_description="' + str(l['description']) + '",'
        #    values += "weather_" + str(l['id']) + '_icon="' + str(l['icon']) +'",'
        try:
            values += "temp="+str(obj['main']['temp'])
        except KeyError as e:
            err=1
        try:
            values += ",tempmax="+str(obj['main']['temp_max'])
        except KeyError as e:
            err=1
        try:
            values += ",humidity="+str(obj['main']['humidity'])
        except KeyError as e:
            err=1
        try:
            values += ",pressure="+str(obj['main']['pressure'])
        except KeyError as e:
            err=1
        try:
            values += ",tempmin="+str(obj['main']['temp_min'])
        except KeyError as e:
            err=1
        try:
            values += ",feelslike="+str(obj['main']['feels_like'])
        except KeyError as e:
            err=1
        try:
            values += ",speed="+str(obj['wind']['speed'])
        except KeyError as e:
            err=1
        try:
            values += ",degrees="+str(obj['wind']['deg'])
        except KeyError as e:
            err=1
        try:
            values += ",sunrise="+str(obj['sys']['sunrise'])
        except KeyError as e:
            err=1
        try:
            values += ",sunset="+str(obj['sys']['sunset'])
        except KeyError as e:
            err=1
        if debugging != 0:
            print("openweathermap,"+tags + values)
        else:
            c = send_to_influxdb()
            c.insert_record("openweathermap," + tags + values)


w()
