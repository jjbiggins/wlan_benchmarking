#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import socket
import urllib.request
import threading
from multiprocessing import Process
import multiprocessing
import subprocess


class NetworkController:
    def __init__(self, curnet=None, nxtnet=None):
        self.curnet = curnet
        self.known_ssids = []
        self.platform = sys.platform
        self.__ssid = self.__get_ssid()
        self.logfile = "netcontroller.log"

    def test_connection(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return [True, ip]
        except OSError:
            return [False, ""]

    def is_macos(self):
        if self.platform is "darwin":
            return True
        else:
            return False
   
    def switch_network(self, **kwargs):
        curnet = kwargs.get("current")
        nxtnet = kwargs.get("next")

        nxtssid = nxtnet['ssid']
        nxtpasswd = nxtnet['passwd']
        
        if self.is_macos():
            subprocess.call(['networksetup', '-setairportnetwork', 'en0',  '{}'.format(nxtssid), '{}'.format(nxtpasswd)])
            wait_for_connection(True)
        else:
            pass
        self.ssid = self.__get_ssid()


    def network_connect(self, **kwargs):
        ssid = kwargs.get("ssid")
        passwd = kwargs.get("passwd")
        exit_code = 1
        if self.is_macos():
            exit_code = subprocess.call(['networksetup', '-setairportnetwork', 'en0',  '{}'.format(ssid), '{}'.format(passwd)])
        else:
            pass

        if exit_code == 0:
            self.__ssid = ssid


    def __init_wlan(self):
        for known_ssid in self.known_ssids:
            if test_connection()[0]:
                continue
            else:
                network_connect(ssid=known_ssid['ssid'],passwd=known_ssid['passwd']):

    def __get_ssid(self):
        ssid = ""
        if self.platform.lower() is 'darwin':   
            cmd = "networksetup -getairportnetwork en0 | cut -d ':' -f2"
            ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            ssid = output.decode("utf-8").strip()
        elif self.platform.lower() is 'linux':
            cmd = 'iw dev wlan0 link'
            ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            ssid = output

        if ssid is "Not Connected." or ssid is None or ssid is "":
            self.__init_wlan(self)

        return ssid


def test_connection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return [True, ip]
    except OSError:
        return [False, ""]

def test_latency(*args):
    sentry, start, end = args[0], args[1], args[2]
    with open("latency.txt", "a") as log:
        while sentry < 2:
            conn = test_connection()
            if conn[0]:
                time = datetime.now()
                if sentry == 1:
                    sentry += 1
                    end = time
                nowtime =  time.strftime("%H:%M:%S.%f")
                #log.write("connected: {}\n".format(nowtime))
            else:
                time = datetime.now()
                if sentry == 0:
                    sentry += 1
                    start = time
                nowtime= time.strftime("%H:%M:%S.%f")
                #log.write("NOT CONNECTED: {}\n".format(nowtime))

        delta = end - start

        log.write("+--------------------------------------------------------------------------------------------------------------+\n")
        log.write("|        {}         |               {}                |       {}         |\n".format(start.strftime("%H:%M:%S.%f"), end.strftime("%H:%M:%S.%f"), delta))


def switch_network(curnet,nxtnet):
    nxtssid = list(nxtnet.keys())[0]
    nxtpasswd = nxtnet[list(nxtnet.keys())[0]]
    subprocess.call(['networksetup', '-setairportnetwork', 'en0',  '{}'.format(nxtssid), '{}'.format(nxtpasswd)])
    wait_for_connection(True)

def wait_for_connection(ip):
    while True:
        conn = test_connection()
        ip = conn[0]
        if ip:
            return
        else:
            pass

def init_network(**kwargs):
    net1={"ATT3KVY7al":"4e#a%fs6kxm6"}
    net2={"MotoVAP_M91329SA11RB":"53464328697643924013131753"}
    if get_ssid() == list(net1.keys())[0]:
        return net1, net2
    else:
        subprocess.call(['networksetup', '-setairportnetwork', 'en0', 'ATT3KVY7al', '4e#a%fs6kxm6'])
        wait_for_connection(True)
        return net1,net2

def get_ssid():
    cmd = "networksetup -getairportnetwork en0 | cut -d ':' -f2"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    ssid = output.decode("utf-8").strip()
    return ssid

def process(curnet,nxtnet,runs):
    for run in range(runs):
        sentry = 0
        start,end = 0,0
        p1 = Process( target=test_latency, args=(sentry, start, end,  ))
        p1.start()
        p2 = Process( target=switch_network, args=(curnet, nxtnet, ))
        p2.start()
        p2.join()
        tmp = curnet
        curnet = nxtnet
        nxtnet = tmp

def main(**kwargs):
    net1,net2 = init_network(ssid="ATT3KVY7al", passwd="4e#a%fs6kxm6")

    curnet=net1
    nxtnet=net2
    with open("latency.txt", "a") as logfile:
        logfile.write("----------------------------------------------------------------------------------------------------------------\n")
        logfile.write("            start                |                   end                        |               delta           \n")

    process(curnet,nxtnet,kwargs.get("runs"))


def ending():
    logfile = open("latency.txt","a")
    logfile.write("+--------------------------------------------------------------------------------------------------------------+\n")
    logfile.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        runs=1
    else:
        runs=int(sys.argv[1])
    main(runs=runs)
