#!/usr/bin/env python

from twisted.scripts.twistd import run
from os.path import join, dirname
from sys import argv
import scrapyd
import sys,os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]

os.chdir(rootPath)



def main():
    argv[1:1] = ['-n', '-y', join(dirname(scrapyd.__file__), 'txapp.py')]
    list1=argv
    print(list1)
    run()

if __name__ == '__main__':
    main()
