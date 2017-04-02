#!/usr/bin/python3
import os
from multiprocessing import Process
import time
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class autorun(object):
    def __init__(self):
        self.cmd = []
        if "--help" in sys.argv or "-h" in sys.argv:
            print("Commandes:")
            print("\twatch          '[filename]'")
            print("\texec           '[CMD]'")
            print("\texec_from_file [filename]")
            exit()
            
        if "watch" in sys.argv :
            self.files = sys.argv[sys.argv.index("watch") + 1].split(";")
            print("Fichiers =",self.files)
        else:
            print("Vous devez indiquer au moins un fichier")
            exit()
            
        if "exec" in sys.argv :
            self.cmd = sys.argv[sys.argv.index("exec") + 1].split(";")
            print("Commandes = ",self.cmd)
        
        if "exec_from_file" in sys.argv:
            self.cmd = open(sys.argv[sys.argv.index("exec_from_file") + 1],"r").read().split("\n")

        self.sub = Process(target=self.sub_)
        self.sub.start()
        self.checker = Process(target=self.check)
        self.checker.start()
    
    def check(self):
        dates = [time.ctime(os.path.getmtime(date)) for date in self.files]
        fmax = max(dates)
        while True:
            if max([time.ctime(os.path.getmtime(date)) for date in self.files])  > fmax :
                self.sub.terminate()
                time.sleep(0.1)
                self.sub = Process(target=self.sub_)
                self.sub.start()
                fmax = max([time.ctime(os.path.getmtime(date)) for date in self.files])
                os.system('cls' if os.name == 'nt' else 'clear')
                print (bcolors.FAIL + bcolors.UNDERLINE + "[Redémarrage]" + bcolors.ENDC)
            time.sleep(1)
        
    def sub_ (self):
        for cmd in self.cmd :
            os.system(cmd)
        print (bcolors.FAIL + bcolors.UNDERLINE + "En attente de changements" + bcolors.ENDC)

autorun()