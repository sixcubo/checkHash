#!/usr/bin/python3
import json
import os
import time
from time import sleep

SHA1_JSON = '#sha1.json'


def jsonNameWithTime():
    return '#sha1_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.json'

def min(l):
    l.sort(reverse=True)

t1 = jsonNameWithTime()
sleep(1)
t2 = jsonNameWithTime()

filenames = [t1, t2]

jsons = [filename for filename in filenames if filename.find('#sha1_', 0, 5)==0]

print(t1.find('#sha1_', 0, 6))

# print(t1)
# print(t2)