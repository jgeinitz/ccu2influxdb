#!/usr/bin/python

import sys
import glob
import os
import calendar
import time
import serial

hygro       = 0
sid         = 0
temperature = 0
new_battery = 0
lowbat      = 0

class DenicWeather:
    global      ser
    verbose     = 0
    quiet       = 0
    temperature = 0.0

    def printYesNo(self,val):
        if val == 1:
            return "yes"
        else:
            return "no"

    def checkcrc(self,telegram):
        return 1

    def reportvalues(self):
        print("SensorID:    "+ str(sid))
        print("New battery: "+ self.printYesNo(new_battery))
        print("low battery: "+ self.printYesNo(lowbat))
        print("Temp:        "+ str(temperature))
        if hygro == 106:
            h="NaN"
        else:
            h=str(hygro)

        print("humidity:    "+h)
        print('\n')

    def reportvaluesLine(self,flux=0):
        global hygro
        global sid
        global temperature
        global new_battery

        if hygro == 106:
            h="-1"
        else:
            h=str(hygro)
        if flux == 0:
            x='sensorid:'+str(sid)+' newbat:'+str(new_battery)+ ' lowbat:'+str(lowbat)+' temp:'+str(temperature) + ' humidity:'+h + ' '
        else:
            x='denicwetter,id='+str(sid)+' sensorid='+str(sid)+',temp='+str(temperature)
        if temperature != 0:
            print(x)
        #sys.stdout.write( x )
        #sys.stdout.flush()

    def reportvaluesCCU(self,flux=0):
        try:
            fil = open("/disk/tmp/DENICt.txt","a+")
            if flux == 0:
                fil.write(str(temperature))
            else:
                ts = int(time.time())
                fil.write('denicwetter,id='+str(sid)+' sensorid='+str(sid)+',temp='+str(temperature) + " " +str(ts) + '000000000')
            fil.write("\n")
            fil.close()
        except:
            error=1

    def tx29parse(self,telegram):
        global sid
        global new_battery
        global temperature
        global lowbat
        global hygro
        global crc

        if telegram[0:1] == '9':
            sid=int(telegram[1:2],16)*4 + ((int(telegram[2:3],16)&0xc)/4)
            try:
                if int(telegram[2:3])&2 :
                    new_battery=1
                else:
                    new_battery=0
            except ValueError as e:
                return 0
            try:
                temperature = ( (float(telegram[3:4])*10) + float(telegram[4:5]) + (float(telegram[5:6])/10.0)) - 40
            except ValueError as e:
                return 0
            try:
                if (int(telegram[6:7])&0x8) != 0:
                    lowbat=1
                else:
                    lowbat=0
            except ValueError as e:
                lowbat = 0
            try:
                hygro= ((int(telegram[6:7])&0x7)<<4)+int(telegram[7:8],16)
            except ValueError:
                hygro = 0
            try:
                crc= (int(telegram[8:9],16)<<4)+int(telegram[9:10],16)
            except ValueError:
                crc=0
            return 1
        else:
            if self.verbose : print 'unknown length '+telegram[0:1]
            return 0

    def culparse(self,telegram):
        if telegram.find('N02',0) == 0 :
            return self.tx29parse(telegram[3:13])
        else:
            if self.verbose:
                print('Unknown CUL Telegram \''+telegram+'\'')
        return 0

    def __init__(self,myname,verb,q):
        self.verbose=verb
        self.quiet=q

        if self.verbose:
            print ('Interface between DENIC Weather Station and influxdb')
            print ('Opening CUL connection')

        p = '/disk/tmp/' + os.path.basename(myname)  + '.pid'
        if os.path.exists(p) :
            if self.verbose:
                print("found pidfile "+ p)
            f = open(p,"r")
            t = f.read()
            try:
                os.kill(int(t),0)
            except OSError as e:
                if e.errno == 3:
                    if self.verbose:
                        print("removing stale pidfile " + p)
                    os.remove(p)
                else:
                    raise
        if not os.path.exists(p):
            if self.verbose:
                print('create pidfile ' + p)
            f = open(p,"w")
            f.write(str(os.getpid()) + '\n')
        else:
            exit(1)
        f.close()
        
            
        # configure the serial connections (the parameters differs on the device you are connecting to)
        for device in glob.glob("/dev/ttyACM*"):
            try:
                self.ser = serial.Serial(
                    port=device,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
            except serial.SerialException as err:
                print ('Cannot open serial line - ', err)
                raise
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

        if self.verbose:
            print('init CUL')
        self.ser.write('X0\r\nX21\r\nNr2\r\nV\r\n')


        #if verbose: print 'Enter your commands below.\nInsert "exit" to leave the application.\n'

    def readloop(self,flux):
        running=1
        input=1
        sleepcounter = 0
        if self.verbose:
            print('entering readloop')
        while running == 1 :
            while self.ser.in_waiting:
                if self.verbose:
                    print("after wait")
                try:
                    out = self.ser.readline()
                except self.ser.SerialException as err:
                    out = ''
                if out != '':
                    if self.verbose:
                        print("rcv: "+str(out))
                    if out.rstrip('\n').rstrip('\r') == "02":
                        if self.verbose:
                            print("init response")
                        running = 1

                    if self.culparse(out.rstrip('\n').rstrip('\r')):
                        if self.checkcrc(out.rstrip('\n').rstrip('\r')):
                            running=0
                        if self.ser.in_waiting > 3 :
                            running=1
                        if self.verbose:
                            self.reportvalues()
                        self.reportvaluesCCU(flux)
                        #if sid != 14 : running = 1
                            #print(sid)
                else:
                    print("empty read")
                    sleepcounter = sleepcounter + 1
                if running == 1:
                    time.sleep(29)
                    sleepcounter = sleepcounter + 1
                    if sleepcounter > 55:
                        if self.verbose:
                            print("read timeout exit")
                            running = 0
                        else:
                            print("timeout")
                            exit(0)

        if self.quiet != 1:
            self.reportvaluesLine(flux)
        self.reportvaluesCCU(flux)


    def finish(self):
        if self.verbose:
            print("turning off receiver")
        self.ser.write("Nx\r\nX00\r\n")
        self.ser.close()

def __main__():
    outputformat = 0
    v = 0
    q = 0
    i_am = sys.argv[0]
    for arg in sys.argv:
        if arg is not '':
            if arg != i_am:
                if arg == "--flux":
                    outputformat=1
                elif arg == "--verbose":
                    v = 1
                elif arg == "-v":
                    v = 1
                elif arg == "--quiet":
                    q = 1
                elif arg == "-q":
                    q = 1
                else:
                    print("usage: "+ i_am + ' [--verbose|-v|--flux]')
                
    x = DenicWeather(i_am,v,q)
    while 1 == 1:
        x.readloop(outputformat)
        if v:
            print("after readloop sleeping")
        time.sleep(99)
    x.finish()

__main__()

