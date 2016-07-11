from PyQt4.QtGui import *
from PyQt4.QtCore import *

import numpy as np
import pyqtgraph as pg
import random
import sys
import datetime

import os
import glob
import time

#Code for temperature logging obtained and modified from https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/overview

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

count = 0
temp_c = 0

class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        
        
        self.home()

    def home(self):    
        
        self.setWindowIcon(QIcon('pythonlogo.png'))
        self.setWindowTitle('Temperature Monitor')
        
        #Grid Layout

        grid = QGridLayout()
               
        #Creating a central widget and applying the grid layout to that 
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(grid)

        #Creating a sub-layout for the LCD Screen and Label

        subLayout = QVBoxLayout()
               
        #Label

        lab1 = QLabel("Sensor 1 Temperature:", self)
        lab1.resize(lab1.sizeHint())

        #LCD Screen widget
        
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(4)

        #Plot widget:
 
        self.continuousPlt = pg.PlotWidget(self)
        self.continuousPlt.setMinimumSize(450,200)
        grid.addWidget(self.continuousPlt, 0,1)
        self.continuousPlt.setYRange(0,100)

        #Timer to update plot and temperature LCD:

        self.timer3 = pg.QtCore.QTimer()
        self.timer3.timeout.connect(self.read_temp)
        self.timer3.start(1000)

        #Add the label and LCD screen to the sub-layout box 

        subLayout.addWidget(lab1)
        subLayout.addWidget(self.lcd)

        #Add the sublayout to the grid

        grid.addLayout(subLayout, 0, 0, 1, 1)
 
        self.show()

    def read_temp_raw(self):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines


    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]

            
            # Attempt to plot against time but problems with plot lag:
            
            #t_now = datetime.datetime.now().time()
            #t_plot = str(t_now.strftime('%H:%M:%S'))
            #(h, m, s) = t_plot.split(':')       #Converting to decimal seconds
            #dec_s = int(s)/60
            #dec_s = "{:.2f}".format(dec_s)
            #t_plot = int(h)*3600+int(m)*60+int(s)
            
            global count
            count = count + 1

            global temp_c
            temp_c_prev = temp_c
            temp_c = float(temp_string) / 1000.0

            print(temp_c)
            
        xt = np.array([count-1,count])
        ytc = np.array([temp_c_prev,temp_c])

        #Auto adjusting the range for 10min period

        if count >30:
            self.continuousPlt.setXRange(count-30,count+30)
        else:
            pass

        if count >1:
            self.continuousPlt.plot(xt,ytc)
            self.lcd.display(temp_c)
            self.continuousPlt.setYRange(temp_c-15,temp_c+15)
        else:
            pass
 
def run():    
        app=QApplication(sys.argv)
        GUI = Window()
        sys.exit(app.exec_())
        
run()
