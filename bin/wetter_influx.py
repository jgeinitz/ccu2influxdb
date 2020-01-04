#!/usr/bin/python3
import json
import pycurl


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
        tags = "coordlon="+ str(obj['coord']['lon'])+","+"coordlat="+str(obj['coord']['lat'])
        tags += ",name=\""+ str(obj['name']) + '"'
        for l in obj['weather']:
            values += "weather_" + str(l['id']) + '_main="' + str(l['main']) +'",'
            values += "weather_" + str(l['id']) + '_description="' + str(l['description']) + '",'
            values += "weather_" + str(l['id']) + '_icon="' + str(l['icon']) +'"'
        values += ",main_temp="+str(obj['main']['temp'])
        values += ",main_tempmax="+str(obj['main']['temp_max'])
        values += ",main_humidity="+str(obj['main']['humidity'])
        values += ",main_pressure="+str(obj['main']['pressure'])
        values += ",main_tempmin="+str(obj['main']['temp_min'])
        values += ",main_feelslike="+str(obj['main']['feels_like'])
        values += ",wind_speed="+str(obj['wind']['speed'])
        values += ",wind_degrees="+str(obj['wind']['deg'])
        values += ",sunrise="+str(obj['sys']['sunrise'])
        values += ",sunset="+str(obj['sys']['sunset'])
        print "openweathermap,"+tags + values
        c = send_to_influxdb()
        c.insert_record("openweathermap," + tags + values)


w()
